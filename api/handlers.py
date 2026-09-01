from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from data.collections import (
    services,
    application,
    application_services,
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "services": services
        }
    )


@router.get("/service/{service_id}")
def service_detail(
    request: Request,
    service_id: int,
):
    service = next(
        (
            service
            for service in services
            if service["id"] == service_id
        ),
        None
    )

    if service is None:
        return {"error": "Услуга не найдена"}

    return templates.TemplateResponse(
        request=request,
        name="service.html",
        context={
            "service": service
        }
    )


@router.get("/application")
def application_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="application.html",
        context={
            "application": application,
            "application_services": application_services,
        }
    )


@router.get("/application/new")
def new_application(
    request: Request,
    service_id: int | None = None,
):
    return templates.TemplateResponse(
        request=request,
        name="application_form.html",
        context={
            "services": services,
            "selected_service_id": service_id,
        }
    )


@router.post("/application/create")
def create_application(
    text: str = Form(...),
    comment: str = Form(""),
    service_ids: list[int] = Form([]),
):
    selected_services = []

    for service in services:
        if service["id"] in service_ids:
            selected_services.append(
                {
                    "service": service,
                    "result": None,
                }
            )

    application["id"] += 1
    application["text"] = text
    application["status"] = "Новая"
    application["comment"] = comment

    application_services.clear()
    application_services.extend(selected_services)

    return RedirectResponse(
        url="/application",
        status_code=303,
    )