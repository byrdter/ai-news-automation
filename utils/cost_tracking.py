"""
Cost tracking utilities for monitoring API usage and expenses.

Tracks costs across all AI models and services to stay within budget.
"""

import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from pathlib import Path

from config.settings import get_settings

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """Supported AI services."""
    OPENAI = "openai"
    COHERE = "cohere"
    ANTHROPIC = "anthropic"
    SUPABASE = "supabase"
    EMAIL = "email"
    OTHER = "other"


@dataclass
class CostEntry:
    """Individual cost tracking entry."""
    timestamp: datetime
    service: ServiceType
    operation: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'service': self.service.value,
            'operation': self.operation,
            'model': self.model,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_tokens': self.total_tokens,
            'cost_usd': self.cost_usd,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CostEntry':
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            service=ServiceType(data['service']),
            operation=data['operation'],
            model=data['model'],
            input_tokens=data['input_tokens'],
            output_tokens=data['output_tokens'],
            total_tokens=data['total_tokens'],
            cost_usd=data['cost_usd'],
            metadata=data.get('metadata', {})
        )


class CostTracker:
    """Cost tracking and budget management."""
    
    # Pricing data (USD per token) - Updated for 2025
    PRICING = {
        ServiceType.OPENAI: {
            'gpt-4o': {'input': 0.0000025, 'output': 0.000010},
            'gpt-4o-mini': {'input': 0.000000150, 'output': 0.000000600},
            'gpt-4-turbo': {'input': 0.000010, 'output': 0.000030},
            'gpt-3.5-turbo': {'input': 0.0000015, 'output': 0.000002},
            'text-embedding-3-small': {'input': 0.00000002, 'output': 0},
            'text-embedding-3-large': {'input': 0.00000013, 'output': 0}
        },
        ServiceType.COHERE: {
            'command-r7b-12-2024': {'input': 0.00000015, 'output': 0.0000006},
            'command-r': {'input': 0.0000005, 'output': 0.000015},
            'command': {'input': 0.000001, 'output': 0.000002},
            'embed-english-v3.0': {'input': 0.0000001, 'output': 0},
            'embed-multilingual-v3.0': {'input': 0.0000001, 'output': 0}
        },
        ServiceType.ANTHROPIC: {
            'claude-3-5-sonnet-20241022': {'input': 0.000003, 'output': 0.000015},
            'claude-3-haiku-20240307': {'input': 0.00000025, 'output': 0.00000125}
        }
    }
    
    def __init__(self):
        """Initialize cost tracker."""
        self.settings = get_settings()
        self.entries: List[CostEntry] = []
        self.session_start = datetime.now(timezone.utc)
        
        # Cost file for persistence
        self.cost_file = Path("data/cost_tracking.json")
        self.cost_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_cost_data()
        
        # Alerts
        self.daily_alert_sent = False
        self.monthly_alert_sent = False
    
    def _load_cost_data(self):
        """Load cost data from file."""
        if self.cost_file.exists():
            try:
                import builtins
                with builtins.open(self.cost_file, 'r') as f:
                    data = json.load(f)
                    self.entries = [CostEntry.from_dict(entry) for entry in data.get('entries', [])]
                logger.info(f"Loaded {len(self.entries)} cost entries")
            except Exception as e:
                logger.error(f"Failed to load cost data: {e}")
                self.entries = []
    
    def _save_cost_data(self):
        """Save cost data to file."""
        try:
            # Skip saving if Python is shutting down
            import sys
            if sys.meta_path is None:
                return
                
            data = {
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'entries': [entry.to_dict() for entry in self.entries]
            }
            # Use builtins.open to avoid any potential shadowing issues
            import builtins
            with builtins.open(self.cost_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            # Don't log errors during Python shutdown
            import sys
            if sys.meta_path is not None:
                logger.error(f"Failed to save cost data: {e}")
    
    def calculate_cost(self, 
                      service: ServiceType, 
                      model: str, 
                      input_tokens: int, 
                      output_tokens: int) -> float:
        """Calculate cost for API call."""
        if service not in self.PRICING:
            logger.warning(f"No pricing data for service {service}")
            return 0.0
        
        model_pricing = self.PRICING[service].get(model)
        if not model_pricing:
            logger.warning(f"No pricing data for model {model}")
            return 0.0
        
        input_cost = input_tokens * model_pricing['input']
        output_cost = output_tokens * model_pricing['output']
        
        return input_cost + output_cost
    
    def track_operation(self,
                       operation: str,
                       service: ServiceType,
                       model: str,
                       input_tokens: int,
                       output_tokens: int = 0,
                       cost_usd: Optional[float] = None,
                       **metadata) -> CostEntry:
        """Track a single operation cost."""
        
        # Calculate cost if not provided
        if cost_usd is None:
            cost_usd = self.calculate_cost(service, model, input_tokens, output_tokens)
        
        entry = CostEntry(
            timestamp=datetime.now(timezone.utc),
            service=service,
            operation=operation,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=cost_usd,
            metadata=metadata
        )
        
        self.entries.append(entry)
        
        # Check budgets
        self._check_budget_alerts()
        
        # Save periodically
        if len(self.entries) % 10 == 0:
            self._save_cost_data()
        
        logger.debug(f"Tracked {operation}: ${cost_usd:.6f} ({input_tokens}/{output_tokens} tokens)")
        
        return entry
    
    def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """Get total cost for a specific day."""
        if date is None:
            date = datetime.now(timezone.utc)
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        daily_entries = [
            entry for entry in self.entries
            if start_date <= entry.timestamp < end_date
        ]
        
        return sum(entry.cost_usd for entry in daily_entries)
    
    def get_monthly_cost(self, year: int, month: int) -> float:
        """Get total cost for a specific month."""
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        
        monthly_entries = [
            entry for entry in self.entries
            if start_date <= entry.timestamp < end_date
        ]
        
        return sum(entry.cost_usd for entry in monthly_entries)
    
    def get_cost_by_service(self, 
                           start_date: datetime, 
                           end_date: datetime) -> Dict[ServiceType, float]:
        """Get cost breakdown by service for date range."""
        filtered_entries = [
            entry for entry in self.entries
            if start_date <= entry.timestamp < end_date
        ]
        
        service_costs = {}
        for entry in filtered_entries:
            if entry.service not in service_costs:
                service_costs[entry.service] = 0.0
            service_costs[entry.service] += entry.cost_usd
        
        return service_costs
    
    def get_cost_by_model(self, 
                         start_date: datetime, 
                         end_date: datetime) -> Dict[str, float]:
        """Get cost breakdown by model for date range."""
        filtered_entries = [
            entry for entry in self.entries
            if start_date <= entry.timestamp < end_date
        ]
        
        model_costs = {}
        for entry in filtered_entries:
            if entry.model not in model_costs:
                model_costs[entry.model] = 0.0
            model_costs[entry.model] += entry.cost_usd
        
        return model_costs
    
    def get_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get usage statistics for the last N days."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        filtered_entries = [
            entry for entry in self.entries
            if start_date <= entry.timestamp < end_date
        ]
        
        if not filtered_entries:
            return {
                'total_cost': 0.0,
                'total_tokens': 0,
                'avg_cost_per_day': 0.0,
                'operations_count': 0,
                'by_service': {},
                'by_model': {}
            }
        
        total_cost = sum(entry.cost_usd for entry in filtered_entries)
        total_tokens = sum(entry.total_tokens for entry in filtered_entries)
        
        return {
            'period_days': days,
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'avg_cost_per_day': total_cost / days,
            'operations_count': len(filtered_entries),
            'avg_cost_per_operation': total_cost / len(filtered_entries),
            'avg_tokens_per_operation': total_tokens / len(filtered_entries),
            'by_service': self.get_cost_by_service(start_date, end_date),
            'by_model': self.get_cost_by_model(start_date, end_date)
        }
    
    def _check_budget_alerts(self):
        """Check if budget alerts should be sent."""
        today_cost = self.get_daily_cost()
        current_month = datetime.now(timezone.utc)
        monthly_cost = self.get_monthly_cost(current_month.year, current_month.month)
        
        # Daily budget alert
        daily_threshold = self.settings.daily_budget_usd * self.settings.cost_alert_threshold
        if today_cost >= daily_threshold and not self.daily_alert_sent:
            self._send_cost_alert(f"Daily budget alert: ${today_cost:.2f} / ${self.settings.daily_budget_usd:.2f}")
            self.daily_alert_sent = True
        
        # Monthly budget alert  
        monthly_threshold = (self.settings.daily_budget_usd * 30) * self.settings.cost_alert_threshold
        if monthly_cost >= monthly_threshold and not self.monthly_alert_sent:
            self._send_cost_alert(f"Monthly budget alert: ${monthly_cost:.2f} / ${self.settings.daily_budget_usd * 30:.2f}")
            self.monthly_alert_sent = True
        
        # Reset daily alert at midnight
        if datetime.now(timezone.utc).hour == 0 and datetime.now(timezone.utc).minute < 5:
            self.daily_alert_sent = False
    
    def _send_cost_alert(self, message: str):
        """Send cost alert (placeholder for email/webhook)."""
        logger.warning(f"COST ALERT: {message}")
        # TODO: Implement email/webhook alerts
    
    def is_daily_budget_exceeded(self) -> bool:
        """Check if daily budget is exceeded."""
        return self.get_daily_cost() >= self.settings.daily_budget_usd
    
    def is_monthly_budget_exceeded(self) -> bool:
        """Check if monthly budget is exceeded."""
        current_month = datetime.now(timezone.utc)
        monthly_cost = self.get_monthly_cost(current_month.year, current_month.month)
        return monthly_cost >= (self.settings.daily_budget_usd * 30)
    
    def get_remaining_daily_budget(self) -> float:
        """Get remaining daily budget."""
        return max(0.0, self.settings.daily_budget_usd - self.get_daily_cost())
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get comprehensive budget status."""
        today_cost = self.get_daily_cost()
        current_month = datetime.now(timezone.utc)
        monthly_cost = self.get_monthly_cost(current_month.year, current_month.month)
        
        daily_limit = self.settings.daily_budget_usd
        monthly_limit = daily_limit * 30
        
        return {
            'daily': {
                'spent': today_cost,
                'limit': daily_limit,
                'remaining': max(0.0, daily_limit - today_cost),
                'percentage': (today_cost / daily_limit) * 100 if daily_limit > 0 else 0,
                'exceeded': today_cost >= daily_limit
            },
            'monthly': {
                'spent': monthly_cost,
                'limit': monthly_limit,
                'remaining': max(0.0, monthly_limit - monthly_cost),
                'percentage': (monthly_cost / monthly_limit) * 100 if monthly_limit > 0 else 0,
                'exceeded': monthly_cost >= monthly_limit
            }
        }
    
    def cleanup_old_entries(self, days_to_keep: int = 90):
        """Remove old cost entries to manage file size."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        
        initial_count = len(self.entries)
        self.entries = [entry for entry in self.entries if entry.timestamp >= cutoff_date]
        removed_count = initial_count - len(self.entries)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} old cost entries")
            self._save_cost_data()
    
    def export_cost_report(self, days: int = 30) -> str:
        """Export cost report as formatted string."""
        stats = self.get_usage_stats(days)
        budget_status = self.get_budget_status()
        
        report = f"""
AI News System - Cost Report ({days} days)
═══════════════════════════════════════

BUDGET STATUS:
Daily: ${budget_status['daily']['spent']:.2f} / ${budget_status['daily']['limit']:.2f} ({budget_status['daily']['percentage']:.1f}%)
Monthly: ${budget_status['monthly']['spent']:.2f} / ${budget_status['monthly']['limit']:.2f} ({budget_status['monthly']['percentage']:.1f}%)

USAGE STATISTICS:
Total Cost: ${stats['total_cost']:.2f}
Total Tokens: {stats['total_tokens']:,}
Operations: {stats['operations_count']:,}
Avg Cost/Day: ${stats['avg_cost_per_day']:.2f}
Avg Cost/Operation: ${stats['avg_cost_per_operation']:.4f}

BY SERVICE:
"""
        
        for service, cost in stats['by_service'].items():
            percentage = (cost / stats['total_cost']) * 100 if stats['total_cost'] > 0 else 0
            report += f"  {service.value}: ${cost:.2f} ({percentage:.1f}%)\n"
        
        report += "\nBY MODEL:\n"
        for model, cost in stats['by_model'].items():
            percentage = (cost / stats['total_cost']) * 100 if stats['total_cost'] > 0 else 0
            report += f"  {model}: ${cost:.2f} ({percentage:.1f}%)\n"
        
        return report
    
    def __del__(self):
        """Ensure cost data is saved on destruction."""
        try:
            self._save_cost_data()
        except:
            pass


# Global cost tracker instance
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker


# Export main components
__all__ = [
    'CostTracker',
    'CostEntry', 
    'ServiceType',
    'get_cost_tracker'
]