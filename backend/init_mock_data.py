import asyncio
from app.database.database import AsyncSessionLocal
from app.models.user import User
from uuid import UUID
from sqlalchemy import select

async def create_mock_user():
    mock_id = UUID('00000000-0000-0000-0000-000000000000')
    async with AsyncSessionLocal() as session:
        # Check if user already exists
        result = await session.execute(select(User).where(User.id == mock_id))
        user = result.scalars().first()
        
        if not user:
            user = User(
                id=mock_id,
                email='mock@example.com',
                password_hash='mock',
                is_active=True
            )
            session.add(user)
            await session.commit()
            print(f"Mock user created with ID: {mock_id}")
        else:
            print(f"Mock user already exists with ID: {mock_id}")

if __name__ == "__main__":
    asyncio.run(create_mock_user())
