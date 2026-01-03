"""
Export/Import API (US11).

Task: US11 - JSON export/import of user data
Spec: specs/features/task-crud.md
"""
import json
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from models import Task
from db import get_session
from middleware.auth import verify_token

router = APIRouter(prefix="/api", tags=["export_import"])


@router.get("/{user_id}/export/json")
async def export_tasks_json(
    user_id: str,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Export user tasks to JSON file (US11).
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    query = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(query).all()

    # Convert to serializable format
    data = [t.model_dump() for t in tasks]

    # Convert datetime objects to string
    for item in data:
        for key, value in item.items():
            if isinstance(value, datetime):
                item[key] = value.isoformat()

    json_content = json.dumps(data, indent=2)

    return StreamingResponse(
        io.BytesIO(json_content.encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=tasks_export_{user_id}.json"}
    )


@router.get("/{user_id}/export/csv")
async def export_tasks_csv(
    user_id: str,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Export user tasks to CSV file (US11).
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    query = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(query).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow(["id", "title", "description", "completed", "priority", "due_date", "tags"])

    for t in tasks:
        writer.writerow([
            t.id,
            t.title,
            t.description or "",
            t.completed,
            t.priority,
            t.due_date.isoformat() if t.due_date else "",
            ",".join(t.tags) if t.tags else ""
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=tasks_export_{user_id}.csv"}
    )


@router.post("/{user_id}/import/json")
async def import_tasks_json(
    user_id: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_token)
):
    """
    Import tasks from a JSON file (US11).
    """
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    try:
        contents = await file.read()
        data = json.loads(contents)

        if not isinstance(data, list):
            raise ValueError("Invalid format: expected a list of tasks")

        imported_count = 0
        for item in data:
            # Create new task instance, ignoring original IDs
            new_task = Task(
                user_id=user_id,
                title=item.get("title", "Imported Task"),
                description=item.get("description"),
                completed=item.get("completed", False),
                priority=item.get("priority", "none"),
                due_date=datetime.fromisoformat(item["due_date"]) if item.get("due_date") else None,
                tags=item.get("tags", []),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_task)
            imported_count += 1

        session.commit()

        return {"message": f"Successfully imported {imported_count} tasks"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error importing file: {str(e)}"
        )
