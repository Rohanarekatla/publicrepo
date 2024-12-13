def get_adp_applications(access_token):
    """
    Get all enterprise applications with ADP AZURE or ADP AWS in their names
    """
    graph_url = "https://graph.microsoft.com/v1.0/servicePrincipals"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get all apps and filter in Python
        response = requests.get(graph_url, headers=headers)
        response.raise_for_status()
        all_apps = response.json().get('value', [])
        
        # Filter for ADP AZURE and ADP AWS
        filtered_apps = [
            app for app in all_apps 
            if 'displayName' in app and 
            ('ADP AZURE' in app['displayName'] or 'ADP AWS' in app['displayName'])
        ]
        
        print(f"Found applications: {[app['displayName'] for app in filtered_apps]}")
        return filtered_apps
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching applications: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response content: {e.response.text}")
        return []
