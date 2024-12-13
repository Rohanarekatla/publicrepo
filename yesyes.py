import requests
import json
import time

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

def get_adp_applications(access_token):
    """
    Get all enterprise applications with ADP AZURE or ADP AWS in their names
    """
    graph_url = "https://graph.microsoft.com/v1.0/servicePrincipals"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        '$filter': "startswith(displayName, 'ADP AZURE') or startswith(displayName, 'ADP AWS')",
        '$select': 'id,displayName,appId,appRoles'
    }
    
    try:
        response = requests.get(graph_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('value', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching applications: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response content: {e.response.text}")
        return []

def read_groups_from_file(file_path):
    """
    Read group names from file, ignoring 'read' and 'write' suffixes
    """
    groups = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split()
                    if parts:
                        group_name = parts[0]
                        groups.append(group_name)
                        print(f"Found group: {group_name}")
        return groups
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return []

def get_group_id(access_token, group_name):
    """
    Get group ID from group name
    """
    graph_url = "https://graph.microsoft.com/v1.0/groups"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        '$filter': f"displayName eq '{group_name}'",
        '$select': 'id,displayName'
    }
    
    try:
        response = requests.get(graph_url, headers=headers, params=params)
        response.raise_for_status()
        groups = response.json().get('value', [])
        if groups:
            print(f"Found group ID for {group_name}: {groups[0]['id']}")
            return groups[0]['id']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting group {group_name}: {str(e)}")
        return None

def check_group_assignment(access_token, sp_id, group_id):
    """
    Check if group is already assigned to the application
    """
    graph_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{sp_id}/appRoleAssignedTo"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(graph_url, headers=headers)
        response.raise_for_status()
        assignments = response.json().get('value', [])
        return any(assignment['principalId'] == group_id for assignment in assignments)
    except requests.exceptions.RequestException as e:
        print(f"Error checking assignment: {str(e)}")
        return False

def add_group_to_app(access_token, sp_id, group_id, app):
    """
    Add group to the application using proper app role assignment
    """
    graph_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{sp_id}/appRoleAssignedTo"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Use the default User role ID
    data = {
        "principalId": group_id,
        "resourceId": sp_id,
        "appRoleId": "00000000-0000-0000-0000-000000000000"  # Default User role
    }
    
    try:
        print(f"Attempting to add group {group_id} to application {sp_id}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(graph_url, headers=headers, json=data)
        
        if response.status_code == 201:
            print("Assignment successful")
            return True
        else:
            print(f"Assignment failed with status code: {response.status_code}")
            print(f"Response content: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error adding group: {str(e)}")
        if hasattr(e.response, 'text'):
            print(f"Response content: {e.response.text}")
        return False

def main():
    # Replace these with your actual values
    tenant_id = "your_tenant_id"
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    groups_file_path = "path_to_your_groups_file.txt"
    
    try:
        # Get access token
        print("Getting access token...")
        access_token = get_access_token(tenant_id, client_id, client_secret)
        
        # Get groups from file
        print(f"\nReading groups from file: {groups_file_path}")
        groups = read_groups_from_file(groups_file_path)
        if not groups:
            print("No valid groups found in file")
            return
            
        # Get ADP applications
        print("\nFetching ADP applications...")
        adp_apps = get_adp_applications(access_token)
        if not adp_apps:
            print("No ADP applications found")
            return
            
        print(f"\nFound {len(adp_apps)} ADP applications")
        
        # Process each application
        for app in adp_apps:
            print(f"\nProcessing application: {app['displayName']} (ID: {app['id']})")
            
            # Process each group for this application
            for group_name in groups:
                print(f"\n  Processing group: {group_name}")
                
                # Get group ID
                group_id = get_group_id(access_token, group_name)
                if not group_id:
                    print(f"  Could not find group: {group_name}")
                    continue
                
                # Check if already assigned
                if check_group_assignment(access_token, app['id'], group_id):
                    print(f"  Group '{group_name}' is already assigned to application '{app['displayName']}'")
                else:
                    # Add group to application
                    if add_group_to_app(access_token, app['id'], group_id, app):
                        print(f"  Successfully added group '{group_name}' to application '{app['displayName']}'")
                    else:
                        print(f"  Failed to add group '{group_name}' to application '{app['displayName']}'")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
