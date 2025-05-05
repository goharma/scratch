connect(username, password, url)
domainRuntime()
cd('/AppRuntimeStateRuntime/AppRuntimeStateRuntime')
application_name = 'YourApplicationName'  # Replace with the actual application name
try:
    state = cmo.getCurrentState(application_name)
    print(f"The state of application '{application_name}' is: {state}")
except javax.management.MBeanException, e:
    if 'TargetNotFoundException' in str(e):
        print(f"Application '{application_name}' not found.")
    else:
        print(f"An error occurred: {e}")
except Exception, e:
    print(f"An unexpected error occurred: {e}")
disconnect()
exit()
