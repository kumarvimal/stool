"""
Deployment tasks
~~~~~~~~~~~~~~~~

Custom deployment tasks for this project.
"""

import invoke


@invoke.task(default=True)
def staging(ctx):
    """
    Deploy to staging environment.

    This is the default deploy task.
    """
    deployment = ctx.get("deployment", {})
    staging_host = deployment.get("staging", "staging.example.com")

    print(f"Deploying to staging: {staging_host}")
    print("Steps:")
    print("  1. Building application...")
    print("  2. Running tests...")
    print("  3. Uploading to staging...")
    print("  4. Restarting services...")
    print("✓ Deployment complete!")


@invoke.task()
def production(ctx):
    """
    Deploy to production environment.

    Use with caution!
    """
    deployment = ctx.get("deployment", {})
    prod_host = deployment.get("production", "prod.example.com")

    print(f"⚠️  DEPLOYING TO PRODUCTION: {prod_host}")
    response = input("Are you sure? (yes/no): ").strip().lower()

    if response == "yes":
        print("Steps:")
        print("  1. Building application...")
        print("  2. Running tests...")
        print("  3. Creating backup...")
        print("  4. Uploading to production...")
        print("  5. Restarting services...")
        print("✓ Production deployment complete!")
    else:
        print("Cancelled")


@invoke.task()
def rollback(ctx):
    """
    Rollback to previous version.

    Reverts the last deployment.
    """
    print("Rolling back to previous version...")
    print("Steps:")
    print("  1. Identifying previous version...")
    print("  2. Stopping current services...")
    print("  3. Restoring from backup...")
    print("  4. Restarting services...")
    print("✓ Rollback complete!")
