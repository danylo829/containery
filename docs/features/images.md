# Image Management

Inspect, search, and manage cached Docker images across all connected hosts.

---

## 1. Image List & Search

* **Navigation**: **Images** (Sidebar: **Images**).

### Features

* **Image Table**: Displays Repository Tags, Image ID, Creation Timestamp, and Image Size (in MB/GB).
* **Multi-Host Filtering**: Select specific Docker hosts from the top filter bar to view images on individual machines.
* **Search & Pagination**: Search images by repository name, image tag, or unique Image ID string.

---

## 2. Inspecting Image Details

* **Navigation**: **Images** > **Click Image Tag / ID**.

View build metadata and configuration specs of any cached Docker image:

* **General Info**: Image ID, CPU Architecture (e.g. `amd64`, `arm64`), OS (e.g. `linux`), Docker build version, Author, Comment, Created date, File size.
* **Configuration Specs**:
  * **Repository Tags**: List of all repository tags assigned to this image.
  * **Entrypoint**: Default container entrypoint command list.
  * **Command (`Cmd`)**: Default execution command array.
  * **Environment Variables**: Pre-configured environment variables set inside the image.
  * **Labels**: Build labels (e.g. maintainer, source repository, OCI spec annotations).

---

## 3. Deleting Images

* **Navigation**: **Images** > **Click Delete icon** next to an image entry.

Permanently removes the specified image from the target Docker host to free up disk space.

!!! note
    Images currently attached to running or stopped containers cannot be deleted until the associated containers are removed first.
