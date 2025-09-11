from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import HTTPException, status


class EmployeesRepository:
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        self.collection = collection

    async def create_employee(self, data: Dict[str, Any]) -> Dict[str, Any]:
        jd = data.get("joining_date")
        if isinstance(jd, str):
            data["joining_date"] = datetime.fromisoformat(jd)
        elif jd and not isinstance(jd, datetime):
            data["joining_date"] = datetime.combine(jd, datetime.min.time())
        try:
            await self.collection.insert_one(data)
        except DuplicateKeyError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="employee_id already exists")
        return data

    async def get_by_employee_id(self, employee_id: str) -> Optional[Dict[str, Any]]:
        return await self.collection.find_one({"employee_id": employee_id}, {"_id": 0})

    async def update_employee(self, employee_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        jd = updates.get("joining_date")
        if jd is not None:
            if isinstance(jd, str):
                updates["joining_date"] = datetime.fromisoformat(jd)
            elif not isinstance(jd, datetime):
                updates["joining_date"] = datetime.combine(jd, datetime.min.time())
        result = await self.collection.update_one({"employee_id": employee_id}, {"$set": updates})
        if result.matched_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        doc = await self.get_by_employee_id(employee_id)
        assert doc is not None
        return doc

    async def delete_employee(self, employee_id: str) -> None:
        result = await self.collection.delete_one({"employee_id": employee_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    async def list_by_department(self, department: str, page: int = 1, page_size: int = 10) -> Tuple[List[Dict[str, Any]], int]:
        q = {"department": department}
        total = await self.collection.count_documents(q)
        cursor = (self.collection.find(q, {"_id": 0}).sort("joining_date", -1).skip((page - 1) * page_size).limit(page_size))
        items = [doc async for doc in cursor]
        return items, total

    async def average_salary_by_department(self) -> List[Dict[str, Any]]:
        pipeline = [
            {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}},
            {"$project": {"_id": 0, "department": "$_id", "avg_salary": {"$round": ["$avg_salary", 2]}}},
            {"$sort": {"department": 1}},
        ]
        cursor = self.collection.aggregate(pipeline)
        return [doc async for doc in cursor]

    async def search_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"skills": {"$elemMatch": {"$regex": f"^{skill}$", "$options": "i"}}}, {"_id": 0})
        return [doc async for doc in cursor]