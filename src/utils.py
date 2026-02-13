import json
import logging

logger = logging.getLogger(__name__)

def check_page_status(driver, url):
    """
    Checks if the current page load was blocked or returned a non-200 status.
    Returns a reason string if blocked, or None if OK.
    """
    # 1. Check HTTP Status from Performance Logs (Chrome only)
    try:
        logs = driver.get_log('performance')
        # logger.warning(f"Total performance logs captured: {len(logs)}")
        
        # Iterate backwards to find the most recent main document request
        for entry in reversed(logs):
            try:
                message_json = json.loads(entry['message'])
                message = message_json['message']
                
                if message['method'] == 'Network.responseReceived':
                    params = message['params']
                    # Check if this is the main document request
                    if params.get('type') == 'Document':
                        response = params['params']['response'] if 'response' in params['params'] else params['response']
                        # Verify it matches the current URL or is a navigation
                        if url in response['url'] or response['url'] in url:
                             status = response['status']
                             if status != 200:
                                 return f"HTTP Status {status}"
                             # Found the main doc status, and it is 200, so we can stop checking logs
                             break
            except (KeyError, json.JSONDecodeError):
                continue

    except Exception as e:
        logger.debug(f"Could not retrieve performance logs: {e}")

    # 2. Check Content for Blocking Keywords
    blocking_keywords = [
        "Access Denied",
        "Cloudflare",
        "403 Forbidden",
        "404 Not Found",
        "Challenge Validation",
        "Pardon Our Interruption",
        "One more step",
        "Are you a human?"
    ]
    
    page_source = driver.page_source.lower()
    title = driver.title.lower()
    
    # logger.warning(f"Page Title: {title}")
    # logger.warning(f"Page Source Snippet: {page_source[:200]}")

    for keyword in blocking_keywords:
        # Check title
        if keyword.lower() in title:
             return f"Blocking keyword in title: '{keyword}'"
        
        # Check body (first 10000 chars to cover most block pages)
        if keyword.lower() in page_source[:10000]:
            return f"Blocking keyword in body: '{keyword}'"

    return None
