"""
Example LangGraph Workflow for Content Processing Pipeline
Location: examples/workflows/content_pipeline.py

This demonstrates:
- LangGraph state management and node definitions  
- Error recovery and conditional routing
- Agent coordination through workflow orchestration
- Validation gates and quality control
- Cost optimization through efficient routing
"""

from typing import List, Dict, Any, Optional, Annotated
from typing_extensions import TypedDict
from datetime import datetime
import logging
import asyncio

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from pydantic import BaseModel, Field

# Import our agent types (these would be defined in your actual agents)
from typing import Protocol

class Agent(Protocol):
    """Protocol for agent interface"""
    async def run(self, message: str, **kwargs) -> Any:
        ...

# State models
class Article(BaseModel):
    """Article data structure"""
    id: str
    title: str
    url: str
    source: str
    content: str
    published_date: Optional[datetime] = None
    relevance_score: float = 0.0
    sentiment_score: float = 0.0
    key_entities: List[str] = []
    categories: List[str] = []
    summary: Optional[str] = None
    processed: bool = False
    processing_errors: List[str] = []

class ProcessingState(TypedDict):
    """State for the content processing workflow"""
    # Input data
    raw_articles: List[Dict[str, Any]]
    
    # Processing stages
    filtered_articles: List[Article]
    analyzed_articles: List[Article]
    summarized_articles: List[Article]
    categorized_articles: List[Article]
    
    # Metadata
    processing_stage: str
    error_count: int
    total_articles: int
    start_time: datetime
    
    # Quality metrics  
    avg_relevance_score: float
    processing_success_rate: float
    
    # Agent states
    discovery_agent_ready: bool
    analysis_agent_ready: bool
    summary_agent_ready: bool
    coordinator_agent_ready: bool

# Mock agents for demonstration (replace with actual Pydantic AI agents)
class MockDiscoveryAgent:
    async def run(self, message: str, articles: List[Dict]) -> List[Article]:
        """Mock news discovery and filtering"""
        filtered = []
        for article_data in articles:
            article = Article(
                id=f"art_{len(filtered)}",
                title=article_data.get("title", ""),
                url=article_data.get("url", ""),
                source=article_data.get("source", ""),  
                content=article_data.get("content", ""),
                published_date=datetime.now(),
                relevance_score=0.8  # Mock score
            )
            if article.relevance_score > 0.6:  # Filter threshold
                filtered.append(article)
        return filtered

class MockAnalysisAgent:
    async def run(self, message: str, articles: List[Article]) -> List[Article]:
        """Mock content analysis"""
        for article in articles:
            # Mock analysis
            article.sentiment_score = 0.7  # Mock positive sentiment
            article.key_entities = ["AI", "Machine Learning", "OpenAI"]  # Mock entities
            article.categories = ["Technology", "Artificial Intelligence"]  # Mock categories
        return articles

class MockSummaryAgent:
    async def run(self, message: str, articles: List[Article]) -> List[Article]:
        """Mock article summarization"""
        for article in articles:
            # Mock summary generation
            article.summary = f"Summary of {article.title}: Key AI developments discussed..."
        return articles

# Initialize agents
discovery_agent = MockDiscoveryAgent()
analysis_agent = MockAnalysisAgent()  
summary_agent = MockSummaryAgent()

# Node functions
async def discovery_node(state: ProcessingState) -> ProcessingState:
    """Node for article discovery and initial filtering"""
    try:
        logging.info(f"Processing {len(state['raw_articles'])} raw articles")
        
        # Filter and convert raw articles
        filtered_articles = await discovery_agent.run(
            "Filter articles for AI relevance",
            articles=state["raw_articles"]
        )
        
        logging.info(f"Filtered to {len(filtered_articles)} relevant articles")
        
        return {
            **state,
            "filtered_articles": filtered_articles,
            "processing_stage": "discovery_complete",
            "discovery_agent_ready": True
        }
        
    except Exception as e:
        logging.error(f"Discovery node error: {e}")
        return {
            **state,
            "processing_stage": "discovery_error",
            "error_count": state["error_count"] + 1,
            "discovery_agent_ready": False
        }

async def analysis_node(state: ProcessingState) -> ProcessingState:
    """Node for content analysis"""
    try:
        articles = state["filtered_articles"]
        logging.info(f"Analyzing {len(articles)} articles")
        
        # Perform analysis
        analyzed_articles = await analysis_agent.run(
            "Analyze content for sentiment, entities, and categories",
            articles=articles
        )
        
        # Calculate quality metrics
        total_relevance = sum(a.relevance_score for a in analyzed_articles)
        avg_relevance = total_relevance / len(analyzed_articles) if analyzed_articles else 0
        
        logging.info(f"Analysis complete. Average relevance: {avg_relevance:.2f}")
        
        return {
            **state,
            "analyzed_articles": analyzed_articles,
            "processing_stage": "analysis_complete",
            "analysis_agent_ready": True,
            "avg_relevance_score": avg_relevance
        }
        
    except Exception as e:
        logging.error(f"Analysis node error: {e}")
        return {
            **state,
            "processing_stage": "analysis_error", 
            "error_count": state["error_count"] + 1,
            "analysis_agent_ready": False
        }

async def summarization_node(state: ProcessingState) -> ProcessingState:
    """Node for article summarization"""
    try:
        articles = state["analyzed_articles"]
        logging.info(f"Summarizing {len(articles)} articles")
        
        # Generate summaries
        summarized_articles = await summary_agent.run(
            "Generate concise summaries for articles",
            articles=articles
        )
        
        logging.info("Summarization complete")
        
        return {
            **state,
            "summarized_articles": summarized_articles,
            "processing_stage": "summarization_complete",
            "coordinator_agent_ready": True
        }
        
    except Exception as e:
        logging.error(f"Summarization node error: {e}")
        return {
            **state,
            "processing_stage": "summarization_error",
            "error_count": state["error_count"] + 1
        }

async def quality_gate_node(state: ProcessingState) -> ProcessingState:
    """Quality validation gate"""
    try:
        articles = state.get("summarized_articles", [])
        total_articles = state["total_articles"]
        
        # Calculate success rate
        success_rate = len(articles) / total_articles if total_articles > 0 else 0
        
        # Quality checks
        quality_passed = (
            success_rate >= 0.8 and  # At least 80% success rate
            state["avg_relevance_score"] >= 0.6 and  # Minimum relevance
            state["error_count"] < 3  # Maximum error tolerance
        )
        
        stage = "quality_passed" if quality_passed else "quality_failed"
        
        logging.info(f"Quality gate: {stage} (success_rate: {success_rate:.2f})")
        
        return {
            **state,
            "processing_stage": stage,
            "processing_success_rate": success_rate,
            "categorized_articles": articles  # Final output
        }
        
    except Exception as e:
        logging.error(f"Quality gate error: {e}")
        return {
            **state,
            "processing_stage": "quality_error",
            "error_count": state["error_count"] + 1
        }

async def error_recovery_node(state: ProcessingState) -> ProcessingState:
    """Error recovery and fallback handling"""
    try:
        error_count = state["error_count"]
        stage = state["processing_stage"]
        
        logging.warning(f"Error recovery triggered at stage: {stage}, errors: {error_count}")
        
        if error_count < 3:
            # Try to recover by using cached/partial results
            if "filtered_articles" in state and state["filtered_articles"]:
                # Use filtered articles as fallback  
                return {
                    **state,
                    "categorized_articles": state["filtered_articles"],
                    "processing_stage": "recovered_partial",
                    "processing_success_rate": 0.5  # Partial success
                }
        
        # Complete failure - return minimal results
        return {
            **state,
            "categorized_articles": [],
            "processing_stage": "failed_recovery",
            "processing_success_rate": 0.0
        }
        
    except Exception as e:
        logging.error(f"Error recovery failed: {e}")
        return {
            **state,
            "processing_stage": "fatal_error",
            "categorized_articles": []
        }

# Conditional routing functions
def should_proceed_to_analysis(state: ProcessingState) -> str:
    """Determine if we should proceed to analysis"""
    if state["processing_stage"] == "discovery_error":
        return "error_recovery"
    elif state["filtered_articles"] and len(state["filtered_articles"]) > 0:
        return "analysis"
    else:
        return "error_recovery"

def should_proceed_to_summarization(state: ProcessingState) -> str:
    """Determine if we should proceed to summarization"""
    if state["processing_stage"] == "analysis_error":
        return "error_recovery"
    elif state["analyzed_articles"] and len(state["analyzed_articles"]) > 0:
        return "summarization"
    else:
        return "error_recovery"

def should_proceed_to_quality_gate(state: ProcessingState) -> str:
    """Determine if we should proceed to quality gate"""
    if state["processing_stage"] == "summarization_error":
        return "error_recovery"
    else:
        return "quality_gate"

def determine_final_route(state: ProcessingState) -> str:
    """Determine final routing"""
    stage = state["processing_stage"]
    
    if stage in ["quality_passed", "recovered_partial"]:
        return END
    elif stage in ["quality_failed", "failed_recovery", "fatal_error"]:
        return END
    else:
        return "error_recovery"

# Build the workflow graph
def create_content_processing_workflow():
    """Create and configure the content processing workflow"""
    
    # Initialize the graph
    workflow = StateGraph(ProcessingState)
    
    # Add nodes
    workflow.add_node("discovery", discovery_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("summarization", summarization_node)
    workflow.add_node("quality_gate", quality_gate_node)
    workflow.add_node("error_recovery", error_recovery_node)
    
    # Set entry point
    workflow.set_entry_point("discovery")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "discovery",
        should_proceed_to_analysis,
        {
            "analysis": "analysis",
            "error_recovery": "error_recovery"
        }
    )
    
    workflow.add_conditional_edges(
        "analysis", 
        should_proceed_to_summarization,
        {
            "summarization": "summarization",
            "error_recovery": "error_recovery"
        }
    )
    
    workflow.add_conditional_edges(
        "summarization",
        should_proceed_to_quality_gate,
        {
            "quality_gate": "quality_gate",
            "error_recovery": "error_recovery"
        }
    )
    
    workflow.add_conditional_edges(
        "quality_gate",
        determine_final_route,
        {
            END: END,
            "error_recovery": "error_recovery"
        }
    )
    
    workflow.add_conditional_edges(
        "error_recovery",
        determine_final_route,
        {
            END: END,
            "error_recovery": "error_recovery"  # Prevent infinite loops
        }
    )
    
    # Compile the workflow
    return workflow.compile()

# Usage example
async def process_articles(raw_articles: List[Dict[str, Any]]) -> ProcessingState:
    """Process articles through the complete pipeline"""
    
    # Initialize state
    initial_state: ProcessingState = {
        "raw_articles": raw_articles,
        "filtered_articles": [],
        "analyzed_articles": [],
        "summarized_articles": [],
        "categorized_articles": [],
        "processing_stage": "initialized",
        "error_count": 0,
        "total_articles": len(raw_articles),
        "start_time": datetime.now(),
        "avg_relevance_score": 0.0,
        "processing_success_rate": 0.0,
        "discovery_agent_ready": False,
        "analysis_agent_ready": False,
        "summary_agent_ready": False,
        "coordinator_agent_ready": False
    }
    
    # Create and run workflow
    workflow = create_content_processing_workflow()
    
    try:
        # Execute the workflow
        final_state = await workflow.ainvoke(initial_state)
        
        # Log final results
        processing_time = (datetime.now() - final_state["start_time"]).total_seconds()
        logging.info(f"Processing complete in {processing_time:.2f} seconds")
        logging.info(f"Final stage: {final_state['processing_stage']}")
        logging.info(f"Success rate: {final_state['processing_success_rate']:.2f}")
        logging.info(f"Final articles: {len(final_state['categorized_articles'])}")
        
        return final_state
        
    except Exception as e:
        logging.error(f"Workflow execution failed: {e}")
        raise

# Testing and example usage
async def main():
    """Example usage of the content processing workflow"""
    
    # Sample raw articles
    raw_articles = [
        {
            "title": "OpenAI Announces GPT-5 with Revolutionary Capabilities",
            "url": "https://example.com/gpt5-announcement",
            "source": "OpenAI Blog",
            "content": "OpenAI today announced GPT-5, featuring advanced reasoning capabilities..."
        },
        {
            "title": "Google's New AI Model Surpasses Human Performance",
            "url": "https://example.com/google-ai-breakthrough", 
            "source": "Google AI Blog",
            "content": "Google researchers have developed a new AI model that achieves..."
        },
        {
            "title": "The Future of Autonomous Vehicles",
            "url": "https://example.com/autonomous-vehicles",
            "source": "TechCrunch",
            "content": "Self-driving cars are becoming more sophisticated with each passing year..."
        }
    ]
    
    # Process articles
    try:
        final_state = await process_articles(raw_articles)
        
        # Display results
        print(f"\n=== Processing Results ===")
        print(f"Stage: {final_state['processing_stage']}")
        print(f"Success Rate: {final_state['processing_success_rate']:.1%}")
        print(f"Articles Processed: {len(final_state['categorized_articles'])}")
        print(f"Average Relevance: {final_state['avg_relevance_score']:.2f}")
        
        # Show processed articles
        for article in final_state['categorized_articles']:
            print(f"\n• {article.title}")
            print(f"  Relevance: {article.relevance_score:.2f}")
            print(f"  Sentiment: {article.sentiment_score:.2f}")
            print(f"  Categories: {', '.join(article.categories)}")
            if article.summary:
                print(f"  Summary: {article.summary[:100]}...")
        
    except Exception as e:
        print(f"Processing failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())