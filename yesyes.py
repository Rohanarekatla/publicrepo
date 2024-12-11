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
    graph_url = "https://graph.microsoft.com/v1.0/groups"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        '$filter': f"displayName eq '{group_display_name}'"
    }
    
    response = requests.get(graph_url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error getting group: {response.text}")
        return None
        
    groups = response.json().get('value', [])
    return groups[0]['id'] if groups else None

def get_service_principal_id(access_token, app_display_name):
    """
    Get service principal ID from application display name
    """
    graph_url = "https://graph.microsoft.com/v1.0/servicePrincipals"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        '$filter': f"displayName eq '{app_display_name}'"
    }
    
    response = requests.get(graph_url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error getting service principal: {response.text}")
        return None
        
    service_principals = response.json().get('value', [])
    return service_principals[0]['id'] if service_principals else None

def check_group_assignment(access_token, sp_id, group_id):
    """
    Check if group is already assigned to the application
    """
    graph_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{sp_id}/appRoleAssignedTo"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(graph_url, headers=headers)
    if response.status_code != 200:
        print(f"Error checking assignment: {response.text}")
        return False
        
    assignments = response.json().get('value', [])
    return any(assignment['principalId'] == group_id for assignment in assignments)

def add_group_to_app(access_token, sp_id, group_id):
    """
    Add group to the application as a user assignment
    """
    graph_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{sp_id}/appRoleAssignedTo"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "principalId": group_id,
        "resourceId": sp_id
    }
    
    response = requests.post(graph_url, headers=headers, json=data)
    if response.status_code != 201:
        print(f"Error adding group: {response.text}")
        return False
    return True

def main():
    # Replace these with your actual values
    tenant_id = "your_tenant_id"
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    group_display_name = "your_group_display_name"
    app_display_name = "your_app_display_name"
    
    try:
        # Get access token
        access_token = get_access_token(tenant_id, client_id, client_secret)
        
        # Get group ID and service principal ID
        group_id = get_group_id(access_token, group_display_name)
        sp_id = get_service_principal_id(access_token, app_display_name)
        
        if not group_id:
            print(f"Could not find group with display name: {group_display_name}")
            return
        if not sp_id:
            print(f"Could not find application with display name: {app_display_name}")
            return
        
        # Check if group is already assigned
        if check_group_assignment(access_token, sp_id, group_id):
            print(f"Group '{group_display_name}' is already assigned to application '{app_display_name}'")
        else:
            # Add group to application
            if add_group_to_app(access_token, sp_id, group_id):
                print(f"Successfully added group '{group_display_name}' to application '{app_display_name}'")
            else:
                print("Failed to add group to application")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
