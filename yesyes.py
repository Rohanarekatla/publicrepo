import requests
import json

def get_access_token(tenant_id, client_id, client_secret):
    """
    Get Azure AD access token using client credentials
    """
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    token_response = requests.post(token_url, data=token_data)
    return token_response.json()['access_token']

def get_group_id(access_token, group_display_name):
    """
    Get group ID from display name
    """
    graph_url = f"https://graph.microsoft.com/v1.0/groups"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        '$filter': f"displayName eq '{group_display_name}'"
    }
    
    response = requests.get(graph_url, headers=headers, params=params)
    groups = response.json().get('value', [])
    
    return groups[0]['id'] if groups else None

def get_app_id(access_token, app_display_name):
    """
    Get application ID from display name
    """
    graph_url = f"https://graph.microsoft.com/v1.0/applications"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        '$filter': f"displayName eq '{app_display_name}'"
    }
    
    response = requests.get(graph_url, headers=headers, params=params)
    apps = response.json().get('value', [])
    
    return apps[0]['id'] if apps else None

def check_group_assignment(access_token, app_id, group_id):
    """
    Check if group is already assigned to the application
    """
    graph_url = f"https://graph.microsoft.com/v1.0/applications/{app_id}/owners"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(graph_url, headers=headers)
    owners = response.json().get('value', [])
    
    return any(owner['id'] == group_id for owner in owners)

def add_group_to_app(access_token, app_id, group_id):
    """
    Add group as owner to the application
    """
    graph_url = f"https://graph.microsoft.com/v1.0/applications/{app_id}/owners/$ref"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{group_id}"
    }
    
    response = requests.post(graph_url, headers=headers, json=data)
    return response.status_code == 204

def main():
    # Replace these with your actual values
    tenant_id = "your_tenant_id"
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    group_display_name = "your_group_display_name"
    app_display_name = "your_app_display_name"
    
    # Get access token
    access_token = get_access_token(tenant_id, client_id, client_secret)
    
    # Get group and app IDs
    group_id = get_group_id(access_token, group_display_name)
    app_id = get_app_id(access_token, app_display_name)
    
    if not group_id or not app_id:
        print("Could not find group or application")
        return
    
    # Check if group is already assigned
    if check_group_assignment(access_token, app_id, group_id):
        print(f"Group '{group_display_name}' is already assigned to application '{app_display_name}'")
    else:
        # Add group to application
        if add_group_to_app(access_token, app_id, group_id):
            print(f"Successfully added group '{group_display_name}' to application '{app_display_name}'")
        else:
            print("Failed to add group to application")

if __name__ == "__main__":
    main()
