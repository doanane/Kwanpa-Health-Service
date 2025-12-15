def __init__(self):
    self.sendgrid_client = None
    self.base_url = settings.BASE_URL
    
    try:
        from sendgrid import SendGridAPIClient
        if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY:
            # THIS LINE MUST EXECUTE:
            self.sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            logger.info("SendGrid email service initialized")  # <-- You should see this
        else:
            logger.warning("SendGrid API key not configured")
    except ImportError:
        logger.warning("SendGrid not installed, email service will log only")