"""
Example Direct API Client for Twitter/X Integration
Location: examples/api_clients/twitter_client.py

This demonstrates:
- Direct API integration without third-party tools
- Rate limiting and retry logic
- Cost optimization through efficient API usage
- Error handling and fallback strategies
- Authentication management
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum
import aiohttp
import time
from urllib.parse import urlencode
import hashlib
import hmac
import base64
from contextlib import asynccontextmanager

# Configuration models
@dataclass
class TwitterCredentials:
    """Twitter API credentials"""
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    bearer_token: str

@dataclass 
class TwitterPost:
    """Twitter post data"""
    text: str
    media_ids: Optional[List[str]] = None
    reply_to_id: Optional[str] = None
    quote_tweet_id: Optional[str] = None
    poll_options: Optional[List[str]] = None
    poll_duration_minutes: int = 1440  # 24 hours default

class TwitterPostType(Enum):
    """Types of Twitter posts"""
    TWEET = "tweet"
    THREAD = "thread" 
    REPLY = "reply"
    QUOTE = "quote"

@dataclass
class RateLimitInfo:
    """Rate limit tracking"""
    limit: int
    remaining: int
    reset_at: datetime
    endpoint: str

class TwitterAPIError(Exception):
    """Custom exception for Twitter API errors"""
    def __init__(self, message: str, status_code: int = None, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class TwitterClient:
    """
    Direct Twitter API client with rate limiting and cost optimization
    Avoids third-party services like Buffer/Hootsuite to minimize costs
    """
    
    BASE_URL = "https://api.twitter.com/2"
    UPLOAD_URL = "https://upload.twitter.com/1.1"
    
    def __init__(self, credentials: TwitterCredentials):
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        self.request_count = 0
        self.daily_cost_estimate = 0.0  # Track API usage costs
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()
    
    async def _init_session(self):
        """Initialize HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "User-Agent": "AI-News-Bot/1.0",
                    "Authorization": f"Bearer {self.credentials.bearer_token}"
                }
            )
    
    async def _close_session(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _generate_oauth_signature(self, method: str, url: str, params: Dict[str, str]) -> str:
        """Generate OAuth 1.0a signature for authenticated requests"""
        # OAuth parameters
        oauth_params = {
            'oauth_consumer_key': self.credentials.api_key,
            'oauth_token': self.credentials.access_token,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': hashlib.md5(str(time.time()).encode()).hexdigest(),
            'oauth_version': '1.0'
        }
        
        # Combine all parameters
        all_params = {**params, **oauth_params}
        
        # Create parameter string
        param_string = '&'.join([f"{k}={v}" for k, v in sorted(all_params.items())])
        
        # Create signature base string
        base_string = f"{method.upper()}&{self._percent_encode(url)}&{self._percent_encode(param_string)}"
        
        # Create signing key
        signing_key = f"{self._percent_encode(self.credentials.api_secret)}&{self._percent_encode(self.credentials.access_token_secret)}"
        
        # Generate signature
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        ).decode()
        
        return signature
    
    def _percent_encode(self, text: str) -> str:
        """Percent encode for OAuth"""
        return (
            str(text)
            .replace('+', '%20')
            .replace('*', '%2A')
            .replace('%7E', '~')
        )
    
    async def _check_rate_limit(self, endpoint: str) -> bool:
        """Check if we can make a request to this endpoint"""
        if endpoint in self.rate_limits:
            rate_limit = self.rate_limits[endpoint]
            
            # Check if rate limit has reset
            if datetime.now() >= rate_limit.reset_at:
                del self.rate_limits[endpoint]
                return True
            
            # Check remaining requests
            if rate_limit.remaining <= 0:
                wait_time = (rate_limit.reset_at - datetime.now()).total_seconds()
                logging.warning(f"Rate limit hit for {endpoint}. Waiting {wait_time:.0f} seconds")
                await asyncio.sleep(wait_time + 1)  # Add 1 second buffer
                return True
        
        return True
    
    def _update_rate_limit(self, endpoint: str, headers: Dict[str, str]):
        """Update rate limit information from response headers"""
        if 'x-rate-limit-limit' in headers:
            self.rate_limits[endpoint] = RateLimitInfo(
                limit=int(headers.get('x-rate-limit-limit', 0)),
                remaining=int(headers.get('x-rate-limit-remaining', 0)),
                reset_at=datetime.fromtimestamp(int(headers.get('x-rate-limit-reset', 0))),
                endpoint=endpoint
            )
    
    async def _make_request(self, method: str, endpoint: str, 
                          data: Optional[Dict] = None, 
                          params: Optional[Dict] = None,
                          use_oauth: bool = False) -> Dict[str, Any]:
        """Make authenticated API request with error handling"""
        
        # Ensure session is initialized
        if not self.session:
            await self._init_session()
        
        # Check rate limits
        await self._check_rate_limit(endpoint)
        
        # Build URL
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        
        # Prepare headers
        headers = {}
        
        if use_oauth:
            # Use OAuth 1.0a for write operations
            oauth_params = {}
            if params:
                oauth_params.update(params)
            if data:
                oauth_params.update(data)
            
            signature = self._generate_oauth_signature(method, url, oauth_params)
            
            # Build OAuth header
            oauth_header_params = {
                'oauth_consumer_key': self.credentials.api_key,
                'oauth_token': self.credentials.access_token,
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_timestamp': str(int(time.time())),
                'oauth_nonce': hashlib.md5(str(time.time()).encode()).hexdigest(),
                'oauth_version': '1.0',
                'oauth_signature': signature
            }
            
            oauth_header = 'OAuth ' + ', '.join([f'{k}="{self._percent_encode(v)}"' for k, v in oauth_header_params.items()])
            headers['Authorization'] = oauth_header
        
        # Make request
        try:
            if method.upper() == 'GET':
                response = await self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                if data:
                    headers['Content-Type'] = 'application/json'
                    response = await self.session.post(url, json=data, params=params, headers=headers)
                else:
                    response = await self.session.post(url, params=params, headers=headers)
            else:
                raise TwitterAPIError(f"Unsupported HTTP method: {method}")
            
            # Update rate limit info
            self._update_rate_limit(endpoint, dict(response.headers))
            
            # Track usage for cost estimation
            self.request_count += 1
            self.daily_cost_estimate += 0.001  # Rough estimate per API call
            
            # Handle response
            if response.status == 200 or response.status == 201:
                return await response.json()
            elif response.status == 429:
                # Rate limited - should have been caught earlier
                raise TwitterAPIError("Rate limit exceeded", response.status)
            else:
                error_text = await response.text()
                try:
                    error_data = json.loads(error_text)
                    error_message = error_data.get('detail', error_text)
                except:
                    error_message = error_text
                
                raise TwitterAPIError(
                    f"API request failed: {error_message}",
                    response.status
                )
                
        except aiohttp.ClientError as e:
            raise TwitterAPIError(f"Network error: {str(e)}")
    
    async def get_user_info(self, username: str = None) -> Dict[str, Any]:
        """Get user information (for verification)"""
        endpoint = "users/me" if not username else f"users/by/username/{username}"
        params = {
            "user.fields": "id,name,username,description,public_metrics,verified"
        }
        
        return await self._make_request("GET", endpoint, params=params)
    
    async def create_tweet(self, post: TwitterPost) -> Dict[str, Any]:
        """Create a new tweet"""
        
        # Validate tweet length
        if len(post.text) > 280:
            raise TwitterAPIError("Tweet text exceeds 280 characters")
        
        # Build tweet data
        tweet_data = {
            "text": post.text
        }
        
        # Add media if provided
        if post.media_ids:
            tweet_data["media"] = {"media_ids": post.media_ids}
        
        # Add reply context
        if post.reply_to_id:
            tweet_data["reply"] = {"in_reply_to_tweet_id": post.reply_to_id}
        
        # Add quote tweet
        if post.quote_tweet_id:
            tweet_data["quote_tweet_id"] = post.quote_tweet_id
        
        # Add poll
        if post.poll_options and len(post.poll_options) >= 2:
            tweet_data["poll"] = {
                "options": post.poll_options,
                "duration_minutes": post.poll_duration_minutes
            }
        
        result = await self._make_request("POST", "tweets", data=tweet_data, use_oauth=True)
        
        logging.info(f"Tweet created successfully: {result.get('data', {}).get('id')}")
        return result
    
    async def create_thread(self, tweets: List[str], delay_seconds: int = 2) -> List[Dict[str, Any]]:
        """Create a Twitter thread"""
        
        if not tweets:
            raise TwitterAPIError("Thread must contain at least one tweet")
        
        results = []
        previous_tweet_id = None
        
        for i, tweet_text in enumerate(tweets):
            # Create tweet post
            post = TwitterPost(
                text=f"{tweet_text} ({i+1}/{len(tweets)})" if len(tweets) > 1 else tweet_text,
                reply_to_id=previous_tweet_id
            )
            
            # Create tweet
            result = await self.create_tweet(post)
            results.append(result)
            
            # Get tweet ID for next reply
            previous_tweet_id = result.get('data', {}).get('id')
            
            # Wait between tweets to avoid rate limiting
            if i < len(tweets) - 1:
                await asyncio.sleep(delay_seconds)
        
        logging.info(f"Thread created with {len(results)} tweets")
        return results
    
    async def upload_media(self, media_path: str, media_type: str = "image") -> str:
        """Upload media and return media_id"""
        
        # This is a simplified version - full implementation would handle
        # chunked uploads for large files
        
        try:
            with open(media_path, 'rb') as f:
                media_data = f.read()
            
            # Upload media (simplified)
            url = f"{self.UPLOAD_URL}/media/upload.json"
            
            form_data = aiohttp.FormData()
            form_data.add_field('media', media_data, 
                              filename=media_path.split('/')[-1],
                              content_type=f'{media_type}/jpeg' if media_type == 'image' else 'video/mp4')
            
            headers = {
                'Authorization': f'Bearer {self.credentials.bearer_token}'
            }
            
            async with self.session.post(url, data=form_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['media_id_string']
                else:
                    error_text = await response.text()
                    raise TwitterAPIError(f"Media upload failed: {error_text}")
                    
        except FileNotFoundError:
            raise TwitterAPIError(f"Media file not found: {media_path}")
        except Exception as e:
            raise TwitterAPIError(f"Media upload error: {str(e)}")
    
    async def schedule_tweet(self, post: TwitterPost, scheduled_time: datetime) -> Dict[str, Any]:
        """
        Schedule a tweet for later posting
        Note: Twitter API v2 doesn't support scheduling directly,
        so this would store in database for later processing
        """
        
        # In a real implementation, this would store in your database
        # and have a scheduler service that posts at the right time
        
        schedule_data = {
            "post": {
                "text": post.text,
                "media_ids": post.media_ids,
                "reply_to_id": post.reply_to_id,
                "quote_tweet_id": post.quote_tweet_id
            },
            "scheduled_for": scheduled_time.isoformat(),
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        logging.info(f"Tweet scheduled for {scheduled_time}")
        
        # Return mock response - in real implementation would save to DB
        return {
            "data": {
                "id": f"scheduled_{int(time.time())}",
                "status": "scheduled",
                "scheduled_for": scheduled_time.isoformat()
            }
        }
    
    async def get_analytics(self, tweet_id: str) -> Dict[str, Any]:
        """Get tweet analytics/metrics"""
        
        endpoint = f"tweets/{tweet_id}"
        params = {
            "tweet.fields": "public_metrics,organic_metrics",
            "expansions": "author_id"
        }
        
        return await self._make_request("GET", endpoint, params=params)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "requests_made": self.request_count,
            "estimated_daily_cost": self.daily_cost_estimate,
            "rate_limits": {
                endpoint: {
                    "remaining": info.remaining,
                    "limit": info.limit,
                    "reset_at": info.reset_at.isoformat()
                }
                for endpoint, info in self.rate_limits.items()
            }
        }

# Example usage and patterns
async def example_usage():
    """Example usage of the Twitter client"""
    
    # Initialize credentials (would come from environment/config)
    credentials = TwitterCredentials(
        api_key="your_api_key",
        api_secret="your_api_secret", 
        access_token="your_access_token",
        access_token_secret="your_access_token_secret",
        bearer_token="your_bearer_token"
    )
    
    # Use client with context manager for proper cleanup
    async with TwitterClient(credentials) as client:
        
        try:
            # Post a simple tweet
            post = TwitterPost(
                text="🤖 AI News Update: OpenAI announces GPT-5 with revolutionary capabilities! Full analysis in our daily report. #AI #MachineLearning"
            )
            
            result = await client.create_tweet(post)
            print(f"Tweet posted: {result}")
            
            # Create a thread for longer content
            thread_tweets = [
                "🧵 Thread: Key AI developments this week (1/3)",
                "• OpenAI releases GPT-5 with improved reasoning\n• Google announces Gemini 2.0\n• Meta releases Llama 3.1 (2/3)",
                "These developments signal a major shift in AI capabilities. Full analysis in our weekly report: [link] (3/3)"
            ]
            
            thread_results = await client.create_thread(thread_tweets)
            print(f"Thread created with {len(thread_results)} tweets")
            
            # Get usage statistics
            stats = client.get_usage_stats()
            print(f"Usage stats: {stats}")
            
        except TwitterAPIError as e:
            logging.error(f"Twitter API error: {e.message}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

# Integration with news articles
class NewsToTwitterConverter:
    """Convert news articles to Twitter-optimized content"""
    
    @staticmethod
    def article_to_tweet(article: Dict[str, Any], include_link: bool = True) -> TwitterPost:
        """Convert an article to a tweet"""
        
        title = article.get('title', '')
        url = article.get('url', '')
        summary = article.get('summary', '')
        
        # Create engaging tweet text
        tweet_text = f"🤖 {title}"
        
        # Add emoji based on content
        if 'breakthrough' in title.lower() or 'announces' in title.lower():
            tweet_text = f"🚀 {title}"
        elif 'research' in title.lower():
            tweet_text = f"🔬 {title}"
        
        # Add hashtags
        hashtags = " #AI #MachineLearning #Technology"
        
        # Calculate available space
        available_space = 280 - len(hashtags)
        if include_link:
            available_space -= 23  # Twitter's URL length
        
        # Truncate if necessary
        if len(tweet_text) > available_space:
            tweet_text = tweet_text[:available_space-3] + "..."
        
        # Add link and hashtags
        if include_link and url:
            tweet_text += f"\n\n{url}"
        
        tweet_text += hashtags
        
        return TwitterPost(text=tweet_text)
    
    @staticmethod
    def article_to_thread(article: Dict[str, Any]) -> List[str]:
        """Convert a detailed article to a Twitter thread"""
        
        title = article.get('title', '')
        summary = article.get('summary', '')
        url = article.get('url', '')
        key_points = article.get('key_points', [])
        
        tweets = []
        
        # Thread starter
        tweets.append(f"🧵 Deep Dive: {title}")
        
        # Summary tweet
        if summary and len(summary) > 50:
            summary_text = summary[:250] + ("..." if len(summary) > 250 else "")
            tweets.append(f"📋 Overview: {summary_text}")
        
        # Key points
        if key_points:
            for i, point in enumerate(key_points[:3]):  # Max 3 key points
                point_text = point[:250] + ("..." if len(point) > 250 else "")
                tweets.append(f"• Key Point {i+1}: {point_text}")
        
        # Conclusion with link
        conclusion = f"Read the full analysis here: {url}\n\n#AI #MachineLearning #Technology"
        tweets.append(conclusion)
        
        return tweets

if __name__ == "__main__":
    # Example testing
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())