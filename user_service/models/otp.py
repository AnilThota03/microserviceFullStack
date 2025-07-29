def get_verification_collection():
    # Stub for OTP verification collection
    # Replace with actual DB logic if needed
    class DummyCollection:
        async def insert_one(self, doc):
            return None
    return DummyCollection()
