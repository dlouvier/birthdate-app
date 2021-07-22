provider "google" {
  credentials = "${file("credentials.json")}"
  project     = "birthdate-app-320610"
  region      = "europe-west3"
}

# resource "google_project" "project" {
#   name       = "birthdate-app"
#   project_id = "birthdate-app"
# }

variable "gcp_service_list" {
  description ="The list of apis necessary for the project"
  type = list(string)
  default = [
    "cloudresourcemanager.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "firestore.googleapis.com",
    "appengine.googleapis.com"
  ]
}

resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project = "birthdate-app-320610"
  service = each.key
}

resource "google_app_engine_application" "app" {
  project     = "birthdate-app-320610"
  location_id = "europe-west"
  database_type = "CLOUD_FIRESTORE"
}

resource "google_storage_bucket" "bucket" {
  name = "birthdate-app-320610"
}

resource "google_storage_bucket_object" "archive" {
  name   = "index.zip"
  bucket = google_storage_bucket.bucket.name
  source = "./../artifacts/v1.zip"
}

resource "google_cloudfunctions_function" "function" {
  name        = "birthday-app-function"
  description = "Serverless Python Project Demo"
  runtime     = "python39"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  entry_point           = "app"
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}