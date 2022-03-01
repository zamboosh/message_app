from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict, List


class Item(BaseModel):
    """Class for input messages with validation for field length"""
    sender: str = Query(None, min_length=1, max_length=20)
    recipient: str = Query(None, min_length=1, max_length=20)
    message: str = Query(None, min_length=1, max_length=500)


def main():
    """The main function that creates and returns the FastAPI object"""
    app = FastAPI()

    messages_collection = {}

    @app.get("/", include_in_schema=False)
    def root():
        """Utility method for redirecting to swagger interface"""
        return RedirectResponse(url="/docs")

    @app.get("/messages/get_messages", response_model=List[Dict[str, str]])
    def get_message_by_recipient(recipient: str = Query(None, min_length=1, max_length=20)):
        """API method to get list of messages according to recipient param"""
        try:
            return messages_collection[recipient]
        except KeyError:  # recipient not exists
            raise HTTPException(status_code=400, detail="Recipient not exists")

    @app.post("/messages/send", response_model=Dict[str, str])
    def send_new_message(user_input: Item):
        """API method to send a new message to recipient"""

        # validation check that all the keys exist in body request
        if not user_input.recipient or not user_input.message or not user_input.sender:
            raise HTTPException(status_code=400, detail="Missing parameters, please fill all requested fields")

        # checking if recipient exists in messages_collection dict
        if user_input.recipient in messages_collection:
            messages_collection[user_input.recipient].append(
                {"sender": user_input.sender, "message": user_input.message})
        else:
            # create new key in messages_collection with new payload as the first item in new list
            messages_collection[user_input.recipient] = [{"sender": user_input.sender, "message": user_input.message}]
        return {"status": 'ok'}

    return app


app = main()
