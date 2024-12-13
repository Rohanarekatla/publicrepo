def read_groups_from_file(file_path):
    """
    Read group names from file, ignoring 'read' and 'write' suffixes
    Returns a list of clean group names
    """
    groups = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Split the line and take only the group name part
                group_name = line.strip().split()[0]
                groups.append(group_name)
        return groups
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return []
	def main():
    # Replace these with your actual values
    tenant_id = "your_tenant_id"
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    groups_file_path = "path_to_your_groups_file.txt"  # Replace with your file path
    
    try:
        # Get access token
        access_token = get_access_token(tenant_id, client_id, client_secret)
        
        # Get groups from file
        groups = read_groups_from_file(groups_file_path)
        if not groups:
            print("No groups found in file")
            return
            
        # Get ADP applications
        adp_apps = get_adp_applications(access_token)
        if not adp_apps:
            print("No ADP applications found")
            return
            
        print("\nProcessing applications and groups...")
        
        # Process each application
        for app in adp_apps:
            print(f"\nProcessing application: {app['displayName']}")
            
            # Process each group for this application
            for group_name in groups:
                print(f"  Processing group: {group_name}")
                
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
                    if add_group_to_app(access_token, app['id'], group_id):
                        print(f"  Successfully added group '{group_name}' to application '{app['displayName']}'")
                    else:
                        print(f"  Failed to add group '{group_name}' to application '{app['displayName']}'")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
