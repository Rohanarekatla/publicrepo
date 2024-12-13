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
        # Get all applications
        response = requests.get(graph_url, headers=headers)
        response.raise_for_status()
        all_apps = response.json().get('value', [])
        
        # Filter for apps containing ADP AZURE or ADP AWS
        filtered_apps = [
            app for app in all_apps 
            if ('ADP AZURE' in app.get('displayName', '') or 'ADP AWS' in app.get('displayName', ''))
        ]
        
        print(f"Found {len(filtered_apps)} matching applications:")
        for app in filtered_apps:
            print(f"- {app['displayName']}")
            
        return filtered_apps
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching applications: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response content: {e.response.text}")
        return []
