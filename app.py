from google.cloud import compute_v1

PROJECT_ID = "12345678"
ZONE = "us-central1-a"
INSTANCE_NAME = "your-running-instance"
IMAGE_NAME = "my-app-image"
INSTANCE_TEMPLATE_NAME = "my-instance-template"
INSTANCE_GROUP_NAME = "my-instance-group"
LB_BACKEND_NAME = "my-backend-service"
HEALTH_CHECK_NAME = "my-health-check"

def create_image_from_instance():
    """Create a custom image from an existing running instance"""
    image_client = compute_v1.ImagesClient()
    operation_client = compute_v1.GlobalOperationsClient()

    image = compute_v1.Image()
    image.source_disk = f"projects/{PROJECT_ID}/zones/{ZONE}/disks/{INSTANCE_NAME}"
    image.name = IMAGE_NAME

    operation = image_client.insert(project=PROJECT_ID, image_resource=image)
    operation_client.wait(project=PROJECT_ID, operation=operation.name)
    print(f"✅ Image {IMAGE_NAME} created successfully!")

def create_instance_template():
    """Create an instance template using the custom image"""
    instance_template_client = compute_v1.InstanceTemplatesClient()

    template = compute_v1.InstanceTemplate()
    template.name = INSTANCE_TEMPLATE_NAME
    template.properties = compute_v1.InstanceProperties(
        machine_type="e2-medium",
        disks=[
            compute_v1.AttachedDisk(
                boot=True,
                auto_delete=True,
                initialize_params=compute_v1.AttachedDiskInitializeParams(
                    source_image=f"projects/{PROJECT_ID}/global/images/{IMAGE_NAME}"
                ),
            )
        ],
        network_interfaces=[compute_v1.NetworkInterface(
            network="global/networks/default"
        )],
    )

    operation = instance_template_client.insert(project=PROJECT_ID, instance_template_resource=template)
    print(f"✅ Instance template {INSTANCE_TEMPLATE_NAME} created successfully!")

def create_instance_group():
    """Create a Managed Instance Group (MIG) for Auto Scaling"""
    mig_client = compute_v1.InstanceGroupManagersClient()
    instance_group = compute_v1.InstanceGroupManager(
        name=INSTANCE_GROUP_NAME,
        base_instance_name="mig-instance",
        instance_template=f"projects/{PROJECT_ID}/global/instanceTemplates/{INSTANCE_TEMPLATE_NAME}",
        target_size=2,  # Min number of instances
    )

    operation = mig_client.insert(project=PROJECT_ID, zone=ZONE, instance_group_manager_resource=instance_group)
    print(f"✅ Managed Instance Group {INSTANCE_GROUP_NAME} created!")

def create_health_check():
    """Create a health check for the Load Balancer"""
    health_check_client = compute_v1.HealthChecksClient()

    health_check = compute_v1.HealthCheck(
        name=HEALTH_CHECK_NAME,
        http_health_check=compute_v1.HTTPHealthCheck(port=80, request_path="/health")
    )

    operation = health_check_client.insert(project=PROJECT_ID, health_check_resource=health_check)
    print(f"✅ Health Check {HEALTH_CHECK_NAME} created!")

def create_backend_service():
    """Create a backend service and attach MIG for Load Balancing"""
    backend_service_client = compute_v1.BackendServicesClient()

    backend_service = compute_v1.BackendService(
        name=LB_BACKEND_NAME,
        backends=[compute_v1.Backend(
            group=f"projects/{PROJECT_ID}/zones/{ZONE}/instanceGroups/{INSTANCE_GROUP_NAME}"
        )],
        health_checks=[f"projects/{PROJECT_ID}/global/healthChecks/{HEALTH_CHECK_NAME}"],
    )

    operation = backend_service_client.insert(project=PROJECT_ID, backend_service_resource=backend_service)
    print(f"✅ Backend Service {LB_FrontEND_NAME} created!")

if __name__ == "__main__":
    create_image_from_instance()
    create_instance_template()
    create_instance_group()
    create_health_check()
    create_backend_service()
    print("🚀 Auto Scaling setup with Load Balancer completed!")
