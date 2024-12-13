def get_adp_applications(access_token):
    """
    Get all enterprise applications with ADP AZURE or ADP AWS in their names
    """
    graph_url = "https://graph.microsoft.com/v1.0/servicePrincipals"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Filter for apps containing either "ADP AZURE" or "ADP AWS"
    params = {
        '$filter': "startswith(displayName, 'ADP AZURE') or startswith(displayName, 'ADP AWS')",
        '$select': 'id,displayName,appId,homepage'  # Select specific properties we want to retrieve
    }
    
    try:
        response = requests.get(graph_url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        apps = response.json().get('value', [])
        
        if not apps:
            print("No ADP applications found")
            return []
            
        # Format and return the results
        formatted_apps = []
        for app in apps:
            formatted_apps.append({
                'display_name': app.get('displayName', 'N/A'),
                'app_id': app.get('appId', 'N/A'),
                'object_id': app.get('id', 'N/A'),
                'homepage': app.get('homepage', 'N/A')
            })
            
        return formatted_apps
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching applications: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response content: {e.response.text}")
        return []
