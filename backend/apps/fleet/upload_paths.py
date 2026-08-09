from pathlib import Path


def vehicle_document_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()

    return (
        f"fleet/vehicle_documents/"
        f"{instance.vehicle.id}/"
        f"{instance.scope.lower()}/"
        f"{instance.document_type.lower()}/"
        f"{instance.id}{extension}"
    )