from django.db import connection
from django.http import JsonResponse


def health_check_foo(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    status = "ok" if db_status == "ok" else "error"
    status_code = 200 if status == "ok" else 503

    return JsonResponse(
        {
            "status": status,
            "database": db_status,
        },
        status=status_code,
    )