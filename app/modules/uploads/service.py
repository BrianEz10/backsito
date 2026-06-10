import logging
from fastapi import HTTPException, UploadFile, status
from app.core.errors import http_error


logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024

class UploadService:

    def __init__(self) -> None:
        pass


    def _validate_file(self, file: UploadFile) -> None:
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise http_error(400, f"Tipo de archivo no soportado: {file.content_type}. Permitidos: jpg, jpeg, png, webp", "INVALID_FILE", "file")

    def _validate_file_size(self, content: bytes) -> None:
        if len(content) > MAX_FILE_SIZE:
            raise http_error(400, "Archivo demasiado grande. Máximo 5 MB", "INVALID_FILE", "file")


    def upload_imagen(self, file: UploadFile) -> dict:

        self._validate_file(file)

        content = file.file.read()

        self._validate_file_size(content)

        try:
            import cloudinary
            import cloudinary.uploader

            result = cloudinary.uploader.upload(
                content,
                folder="foodstore/productos",
                allowed_formats=["jpg", "jpeg", "png", "webp"],
                overwrite=False,
                unique_filename=True,
                resource_type="image",
            )

            return {
                "secure_url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "resource_type": result.get("resource_type", "image"),
            }

        except ImportError:
            raise http_error(500, "cloudinary no instalado. pip install cloudinary", "INTERNAL_ERROR")
        
        except Exception as e:
            logger.exception("Error al subir imagen a Cloudinary")
            raise http_error(500, f"Error al subir imagen: {str(e)}", "INTERNAL_ERROR")


    def eliminar_imagen(self, public_id: str) -> None:

        try:
            import cloudinary
            import cloudinary.uploader

            result = cloudinary.uploader.destroy(public_id)

            if result.get("result") != "ok":
                logger.warning("Error al eliminar imagen %s: %s", public_id, result)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se pudo eliminar la imagen: {result.get('result')}")

        except ImportError:
            raise http_error(500, "cloudinary no instalado. pip install cloudinary", "INTERNAL_ERROR")
        
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error al eliminar imagen de Cloudinary")
            raise http_error(500, f"Error al eliminar imagen: {str(e)}", "INTERNAL_ERROR")