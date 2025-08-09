"""
Email Notifications MCP Server.

Provides email delivery tools for reports, alerts, and notifications
using SMTP with template rendering and delivery tracking.
"""

import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import base64
from jinja2 import Environment, FileSystemLoader, Template

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, EmailStr

from config.settings import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Email Notifications")


class EmailRequest(BaseModel):
    """Request to send an email."""
    to_addresses: List[EmailStr] = Field(..., min_items=1, max_items=100)
    subject: str = Field(..., max_length=200)
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    
    # Optional fields
    cc_addresses: List[EmailStr] = Field(default_factory=list, max_items=50)
    bcc_addresses: List[EmailStr] = Field(default_factory=list, max_items=50)
    reply_to: Optional[EmailStr] = None
    
    # Attachments
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Delivery options
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")
    retry_attempts: int = Field(default=3, ge=1, le=10)
    delay_seconds: int = Field(default=0, ge=0, le=3600)


class TemplateEmailRequest(BaseModel):
    """Request to send templated email."""
    template_name: str = Field(..., pattern="^[a-zA-Z0-9_-]+$")
    to_addresses: List[EmailStr] = Field(..., min_items=1, max_items=100)
    subject: str = Field(..., max_length=200)
    template_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Optional fields
    cc_addresses: List[EmailStr] = Field(default_factory=list)
    bcc_addresses: List[EmailStr] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)


class EmailResponse(BaseModel):
    """Response from email sending operation."""
    success: bool
    message: str
    
    # Delivery details
    sent_count: int = Field(default=0)
    failed_count: int = Field(default=0)
    failed_addresses: List[str] = Field(default_factory=list)
    
    # Metrics
    send_time: float = Field(default=0.0)
    email_size_bytes: int = Field(default=0)
    
    # Error details
    errors: List[str] = Field(default_factory=list)


class BulkEmailRequest(BaseModel):
    """Request for bulk email sending."""
    emails: List[EmailRequest] = Field(..., min_items=1, max_items=1000)
    max_concurrent: int = Field(default=5, ge=1, le=20)
    batch_delay_seconds: float = Field(default=1.0, ge=0.1, le=10.0)
    stop_on_error: bool = Field(default=False)


class EmailService:
    """Email service for sending notifications."""
    
    def __init__(self):
        """Initialize email service."""
        self.settings = get_settings()
        self.template_env = self._setup_templates()
        
        # SMTP configuration
        self.smtp_config = {
            'hostname': self.settings.email.smtp_host,
            'port': self.settings.email.smtp_port,
            'username': self.settings.email.smtp_user,
            'password': self.settings.email.smtp_password.get_secret_value() if self.settings.email.smtp_password else None,
            'use_tls': self.settings.email.use_tls,
            'timeout': 30
        }
        
        # Email defaults
        self.from_address = self.settings.email.from_address
        self.from_name = self.settings.email.from_name
        
        # Rate limiting
        self.last_send_time = 0.0
        self.send_count = 0
        self.rate_limit_window = 60.0  # seconds
        self.max_sends_per_window = 100
    
    def _setup_templates(self) -> Environment:
        """Setup Jinja2 template environment."""
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default templates if they don't exist
        self._create_default_templates(template_dir)
        
        return Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def _create_default_templates(self, template_dir: Path):
        """Create default email templates."""
        templates = {
            "daily_report.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .section { margin-bottom: 30px; }
        .article { border-left: 3px solid #e5e7eb; padding-left: 15px; margin-bottom: 15px; }
        .footer { background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; }
        .metrics { background: #f9fafb; padding: 15px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <p>{{ period_start.strftime('%B %d, %Y') }} - {{ period_end.strftime('%B %d, %Y') }}</p>
    </div>
    
    <div class="content">
        <div class="metrics">
            <strong>Report Metrics:</strong>
            {{ total_articles }} articles analyzed | 
            {{ sources_covered }} sources | 
            Average relevance: {{ "%.1f"|format(avg_relevance * 100) }}%
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <p>{{ executive_summary }}</p>
        </div>
        
        {% for section in sections %}
        <div class="section">
            <h2>{{ section.title }}</h2>
            <p>{{ section.content }}</p>
            
            {% for article in section.articles[:5] %}
            <div class="article">
                <h3><a href="{{ article.url }}">{{ article.title }}</a></h3>
                <p><strong>{{ article.source }}</strong> | {{ article.published_date.strftime('%b %d, %Y') }}</p>
                <p>{{ article.summary }}</p>
                {% if article.key_points %}
                <ul>
                {% for point in article.key_points %}
                    <li>{{ point }}</li>
                {% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endfor %}
        
        {% if trends %}
        <div class="section">
            <h2>Trend Analysis</h2>
            {% for trend in trends %}
            <div style="margin-bottom: 15px;">
                <h3>{{ trend.trend_name }}</h3>
                <p>{{ trend.description }} 
                {% if trend.change_direction == 'up' %}📈{% elif trend.change_direction == 'down' %}📉{% else %}➡️{% endif %}
                {{ "%.1f"|format(trend.change_percentage|abs) }}%</p>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if key_insights %}
        <div class="section">
            <h2>Key Insights</h2>
            <ul>
            {% for insight in key_insights %}
                <li>{{ insight }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
    
    <div class="footer">
        <p>Generated by AI News Automation System</p>
        <p>Report ID: {{ metadata.report_id }}</p>
        <p>Generated at {{ metadata.generated_at.strftime('%Y-%m-%d %H:%M UTC') }}</p>
    </div>
</body>
</html>
            """,
            
            "breaking_alert.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>🚨 Breaking AI News Alert</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .alert-header { background: #dc2626; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .urgency-high { border-left: 4px solid #dc2626; }
        .urgency-medium { border-left: 4px solid #f59e0b; }
        .urgency-low { border-left: 4px solid #10b981; }
    </style>
</head>
<body>
    <div class="alert-header">
        <h1>🚨 Breaking AI News Alert</h1>
        <p>{{ alert_time.strftime('%B %d, %Y at %H:%M UTC') }}</p>
    </div>
    
    <div class="content">
        <div class="urgency-{{ urgency_level }}">
            <h2>{{ title }}</h2>
            <p><strong>Source:</strong> {{ source }}</p>
            <p><strong>Published:</strong> {{ published_date.strftime('%B %d, %Y at %H:%M') }}</p>
            
            <h3>Summary</h3>
            <p>{{ summary }}</p>
            
            {% if key_points %}
            <h3>Key Points</h3>
            <ul>
            {% for point in key_points %}
                <li>{{ point }}</li>
            {% endfor %}
            </ul>
            {% endif %}
            
            <h3>Why This Matters</h3>
            <p>{{ impact_analysis }}</p>
            
            <p><a href="{{ url }}" style="background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Read Full Article</a></p>
        </div>
    </div>
</body>
</html>
            """,
            
            "simple_notification.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ subject }}</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <div>{{ content | safe }}</div>
        {% if footer %}
        <hr style="margin: 30px 0;">
        <small>{{ footer }}</small>
        {% endif %}
    </div>
</body>
</html>
            """
        }
        
        for filename, content in templates.items():
            template_file = template_dir / filename
            if not template_file.exists():
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content.strip())
    
    async def rate_limit_check(self):
        """Check and enforce rate limiting."""
        current_time = time.time()
        
        # Reset counter if window expired
        if current_time - self.last_send_time > self.rate_limit_window:
            self.send_count = 0
            self.last_send_time = current_time
        
        # Check rate limit
        if self.send_count >= self.max_sends_per_window:
            wait_time = self.rate_limit_window - (current_time - self.last_send_time)
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                self.send_count = 0
        
        self.send_count += 1
    
    def create_message(self, request: EmailRequest) -> MIMEMultipart:
        """Create email message from request."""
        msg = MIMEMultipart('alternative')
        
        # Headers
        msg['From'] = f"{self.from_name} <{self.from_address}>"
        msg['To'] = ', '.join(request.to_addresses)
        msg['Subject'] = request.subject
        
        if request.cc_addresses:
            msg['Cc'] = ', '.join(request.cc_addresses)
        
        if request.reply_to:
            msg['Reply-To'] = request.reply_to
        
        # Priority
        if request.priority == 'high':
            msg['X-Priority'] = '1'
            msg['Importance'] = 'high'
        elif request.priority == 'low':
            msg['X-Priority'] = '5'
            msg['Importance'] = 'low'
        
        # Content
        if request.text_content:
            text_part = MIMEText(request.text_content, 'plain', 'utf-8')
            msg.attach(text_part)
        
        if request.html_content:
            html_part = MIMEText(request.html_content, 'html', 'utf-8')
            msg.attach(html_part)
        
        # Attachments
        for attachment in request.attachments:
            self._add_attachment(msg, attachment)
        
        return msg
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message."""
        try:
            part = MIMEBase('application', 'octet-stream')
            
            if 'content' in attachment:
                # Base64 encoded content
                content = base64.b64decode(attachment['content'])
                part.set_payload(content)
            elif 'file_path' in attachment:
                # File path
                with open(attachment['file_path'], 'rb') as f:
                    part.set_payload(f.read())
            else:
                logger.warning(f"Invalid attachment format: {attachment}")
                return
            
            encoders.encode_base64(part)
            
            filename = attachment.get('filename', 'attachment')
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Failed to add attachment {attachment}: {e}")
    
    async def send_email(self, request: EmailRequest) -> EmailResponse:
        """Send single email."""
        start_time = time.time()
        
        try:
            # Rate limiting
            await self.rate_limit_check()
            
            # Create message
            message = self.create_message(request)
            message_str = message.as_string()
            
            # All recipients (to, cc, bcc)
            all_recipients = []
            all_recipients.extend(request.to_addresses)
            all_recipients.extend(request.cc_addresses)
            all_recipients.extend(request.bcc_addresses)
            
            # Send email with retry logic
            sent_count = 0
            failed_addresses = []
            errors = []
            
            for attempt in range(request.retry_attempts):
                try:
                    # Connect to SMTP server
                    if self.smtp_config['use_tls']:
                        server = aiosmtplib.SMTP(
                            hostname=self.smtp_config['hostname'],
                            port=self.smtp_config['port'],
                            timeout=self.smtp_config['timeout']
                        )
                        await server.connect()
                        await server.starttls()
                    else:
                        server = aiosmtplib.SMTP(
                            hostname=self.smtp_config['hostname'],
                            port=self.smtp_config['port'],
                            timeout=self.smtp_config['timeout']
                        )
                        await server.connect()
                    
                    # Login if credentials provided
                    if self.smtp_config['username'] and self.smtp_config['password']:
                        await server.login(
                            self.smtp_config['username'],
                            self.smtp_config['password']
                        )
                    
                    # Send message
                    await server.send_message(
                        message,
                        sender=self.from_address,
                        recipients=all_recipients
                    )
                    
                    await server.quit()
                    
                    sent_count = len(all_recipients)
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(error_msg)
                    
                    if attempt < request.retry_attempts - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        failed_addresses = all_recipients
            
            send_time = time.time() - start_time
            
            if sent_count > 0:
                logger.info(f"Email sent successfully to {sent_count} recipients in {send_time:.2f}s")
                return EmailResponse(
                    success=True,
                    message=f"Email sent to {sent_count} recipients",
                    sent_count=sent_count,
                    send_time=send_time,
                    email_size_bytes=len(message_str)
                )
            else:
                logger.error(f"Email sending failed to all recipients: {errors}")
                return EmailResponse(
                    success=False,
                    message="Failed to send email to all recipients",
                    failed_count=len(all_recipients),
                    failed_addresses=all_recipients,
                    send_time=send_time,
                    errors=errors
                )
                
        except Exception as e:
            error_msg = f"Email sending failed: {str(e)}"
            logger.error(error_msg)
            
            return EmailResponse(
                success=False,
                message=error_msg,
                failed_count=len(request.to_addresses),
                failed_addresses=list(request.to_addresses),
                send_time=time.time() - start_time,
                errors=[error_msg]
            )
    
    async def send_templated_email(self, request: TemplateEmailRequest) -> EmailResponse:
        """Send email using template."""
        try:
            # Load and render template
            template = self.template_env.get_template(f"{request.template_name}.html")
            html_content = template.render(**request.template_data)
            
            # Create email request
            email_request = EmailRequest(
                to_addresses=request.to_addresses,
                cc_addresses=request.cc_addresses,
                bcc_addresses=request.bcc_addresses,
                subject=request.subject,
                html_content=html_content,
                attachments=request.attachments
            )
            
            return await self.send_email(email_request)
            
        except Exception as e:
            error_msg = f"Template email sending failed: {str(e)}"
            logger.error(error_msg)
            
            return EmailResponse(
                success=False,
                message=error_msg,
                failed_count=len(request.to_addresses),
                failed_addresses=list(request.to_addresses),
                errors=[error_msg]
            )


# Global email service instance
email_service = EmailService()


@mcp.tool()
async def send_email(request: EmailRequest) -> EmailResponse:
    """
    Send an email with optional HTML/text content and attachments.
    
    Supports multiple recipients, CC/BCC, priorities, and retry logic.
    """
    logger.info(f"Sending email to {len(request.to_addresses)} recipients: {request.subject}")
    
    # Add delay if requested
    if request.delay_seconds > 0:
        await asyncio.sleep(request.delay_seconds)
    
    return await email_service.send_email(request)


@mcp.tool()
async def send_templated_email(request: TemplateEmailRequest) -> EmailResponse:
    """
    Send an email using a predefined template.
    
    Templates support Jinja2 syntax and are stored in templates/email/.
    """
    logger.info(f"Sending templated email '{request.template_name}' to {len(request.to_addresses)} recipients")
    
    return await email_service.send_templated_email(request)


@mcp.tool()
async def send_bulk_emails(request: BulkEmailRequest) -> Dict[str, Any]:
    """
    Send multiple emails with concurrency control and rate limiting.
    
    Processes emails in batches with configurable delays and error handling.
    """
    logger.info(f"Starting bulk email send: {len(request.emails)} emails")
    
    start_time = time.time()
    results = []
    successful_sends = 0
    failed_sends = 0
    
    # Semaphore for concurrency control
    semaphore = asyncio.Semaphore(request.max_concurrent)
    
    async def send_single_email(email_req: EmailRequest, index: int) -> EmailResponse:
        async with semaphore:
            try:
                result = await email_service.send_email(email_req)
                
                # Add delay between sends
                if index < len(request.emails) - 1:  # Don't delay after last email
                    await asyncio.sleep(request.batch_delay_seconds)
                
                return result
                
            except Exception as e:
                logger.error(f"Bulk email {index} failed: {e}")
                return EmailResponse(
                    success=False,
                    message=str(e),
                    failed_count=len(email_req.to_addresses),
                    failed_addresses=list(email_req.to_addresses),
                    errors=[str(e)]
                )
    
    try:
        # Execute all email sends
        tasks = [
            send_single_email(email_req, i) 
            for i, email_req in enumerate(request.emails)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_sends += 1
                final_results.append(EmailResponse(
                    success=False,
                    message=str(result),
                    failed_count=len(request.emails[i].to_addresses),
                    failed_addresses=list(request.emails[i].to_addresses),
                    errors=[str(result)]
                ))
                
                if request.stop_on_error:
                    logger.error(f"Stopping bulk send due to error: {result}")
                    break
                    
            else:
                final_results.append(result)
                if result.success:
                    successful_sends += result.sent_count
                else:
                    failed_sends += result.failed_count
        
        total_time = time.time() - start_time
        
        logger.info(f"Bulk email completed: {successful_sends} sent, {failed_sends} failed in {total_time:.2f}s")
        
        return {
            "success": successful_sends > 0,
            "total_processed": len(final_results),
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
            "processing_time": total_time,
            "results": [result.dict() for result in final_results]
        }
        
    except Exception as e:
        error_msg = f"Bulk email sending failed: {str(e)}"
        logger.error(error_msg)
        
        return {
            "success": False,
            "total_processed": 0,
            "successful_sends": 0,
            "failed_sends": len(request.emails),
            "processing_time": time.time() - start_time,
            "error": error_msg,
            "results": []
        }


@mcp.tool()
async def validate_email_config() -> Dict[str, Any]:
    """
    Validate email configuration and test SMTP connection.
    
    Returns connection status and configuration details.
    """
    logger.info("Validating email configuration")
    
    validation_result = {
        "config_valid": False,
        "smtp_connection": False,
        "templates_available": False,
        "details": {},
        "errors": []
    }
    
    try:
        # Check configuration
        settings = get_settings()
        config_issues = []
        
        if not settings.email.smtp_host:
            config_issues.append("SMTP host not configured")
        if not settings.email.from_address:
            config_issues.append("From address not configured")
        if not settings.email.smtp_user:
            config_issues.append("SMTP username not configured")
        if not settings.email.smtp_password:
            config_issues.append("SMTP password not configured")
        
        validation_result["config_valid"] = len(config_issues) == 0
        if config_issues:
            validation_result["errors"].extend(config_issues)
        
        # Test SMTP connection
        if validation_result["config_valid"]:
            try:
                server = aiosmtplib.SMTP(
                    hostname=settings.email.smtp_host,
                    port=settings.email.smtp_port,
                    timeout=10
                )
                await server.connect()
                
                if settings.email.use_tls:
                    await server.starttls()
                
                if settings.email.smtp_user and settings.email.smtp_password:
                    await server.login(
                        settings.email.smtp_user,
                        settings.email.smtp_password.get_secret_value()
                    )
                
                await server.quit()
                validation_result["smtp_connection"] = True
                
            except Exception as e:
                validation_result["errors"].append(f"SMTP connection failed: {str(e)}")
        
        # Check templates
        try:
            template_dir = Path(__file__).parent.parent / "templates" / "email"
            template_files = list(template_dir.glob("*.html"))
            validation_result["templates_available"] = len(template_files) > 0
            validation_result["details"]["template_count"] = len(template_files)
            validation_result["details"]["templates"] = [f.stem for f in template_files]
            
        except Exception as e:
            validation_result["errors"].append(f"Template validation failed: {str(e)}")
        
        # Configuration details
        validation_result["details"].update({
            "smtp_host": settings.email.smtp_host,
            "smtp_port": settings.email.smtp_port,
            "use_tls": settings.email.use_tls,
            "from_address": settings.email.from_address,
            "from_name": settings.email.from_name
        })
        
        return validation_result
        
    except Exception as e:
        validation_result["errors"].append(f"Validation failed: {str(e)}")
        return validation_result


if __name__ == "__main__":
    # Run the MCP server
    import uvicorn
    from mcp.server.fastmcp import FastMCPServer
    
    settings = get_settings()
    port = getattr(settings.system, 'mcp_email_server_port', 3003)
    
    logger.info(f"Starting Email Notifications MCP Server on port {port}")
    
    # Create FastMCP server instance
    app = FastMCPServer(mcp)
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        reload=False
    )