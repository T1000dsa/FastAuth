from authlib.integrations.starlette_client import OAuth

from src.core.config.config import settings


def register_oauth_providers(oauth: OAuth) -> OAuth:
    # Facebook
    oauth.register(
        name='facebook',
        client_id=settings.facebook.client_id,
        client_secret=settings.facebook.client_secret,
        authorize_url=settings.facebook.authorize_url,
        access_token_url=settings.facebook.access_token_url,
        api_base_url=settings.facebook.api_base_url,
        client_kwargs=settings.facebook.client_kwargs
    )
    
    # GitHub
    oauth.register(
        name='github',
        client_id=settings.github.client_id,
        client_secret=settings.github.client_secret,
        authorize_url=settings.github.authorize_url,
        access_token_url=settings.github.access_token_url,
        api_base_url=settings.github.api_base_url,
        client_kwargs=settings.github.client_kwargs
    )
    
    # StackOverflow
    so_kwargs = settings.stackoverflow.client_kwargs
    if settings.stackoverflow.key:
        so_kwargs['key'] = settings.stackoverflow.key
        
    oauth.register(
        name='stackoverflow',
        client_id=settings.stackoverflow.client_id,
        client_secret=settings.stackoverflow.client_secret,
        authorize_url=settings.stackoverflow.authorize_url,
        access_token_url=settings.stackoverflow.access_token_url,
        api_base_url=settings.stackoverflow.api_base_url,
        client_kwargs=so_kwargs
    )
    
    return oauth