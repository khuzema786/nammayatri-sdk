from locust import HttpUser, task, between
import random
import datetime
import random
import json


class LocationUpdate(HttpUser):
    def on_start(self):
        self.token = [
            "5e74a3e6-d0f9-4568-8d49-0e8b765cfb97",
            "526c2355-1eb4-41fc-8703-26aa808e802f",
            "50e0dead-45ae-404e-b787-8073bfc40ab0",
            "8a348d9c-5360-404a-8687-3edf612f4a42",
            "6067522b-819a-4fab-821a-9caa73b15b69",
            "1290d93f-2c95-43b5-823d-cc9ee5396316",
            "ae0d6fe9-8e1d-4386-9b6a-d9993c5299b6",
            "2f834b4e-ef4d-4713-b91c-68663a429a9b",
            "3caf46c1-8d55-45f1-b3ac-047249ad1b80",
            "0e17afaa-94f6-44ff-a1de-d97357afbe85",
            "b72e32ae-dd1a-49bb-8863-855c65717a43",
            "16a25d98-843d-419d-9c50-b7b805454040",
            "6c6cd6d6-e81c-4ac5-a8dc-344f30d6cce4",
            "c1c09d3e-aa2f-4d81-8ef7-ce4e7cbc1fd8",
            "6c9131e5-1b3b-442c-9aa9-849778fb5f80",
            "566b6809-dd24-405f-9683-7e8f899fb1e8",
            "f7c8c096-45a1-4789-87ca-10c39963d076",
            "778946f4-bb6c-4a40-b5ce-dae8c717bfb7",
            "1fc71f3e-27a0-4177-b0a6-804eb3272973",
            "aae50268-1c21-49db-b9c6-dd3e840bbb27",
            "46cc23e2-6f66-4a14-9847-9262b89502b3",
            "5fb86bc1-b389-406a-8a75-5bea26d143d3",
            "ae471323-4c9b-46fe-80a6-e85176e778c9",
            "1b16a562-a537-4b68-9d6a-2f2fb9192c0e",
            "d759b3d8-f3fc-4ceb-aa2f-33cdfb6a3eaf",
            "b2e759a2-c6b3-4289-9d53-b127492e1fce",
            "b799435c-ca42-4cfa-8e61-457f9001e96f",
            "7dc764ef-a5a6-44da-a24d-1b944de149d0",
            "2e918336-848f-4782-bdd6-13d14563eb37",
            "5eca51c3-d4df-46fb-8122-d8ac21d7f4fa",
            "82b77c7f-00cb-4553-a036-64bbf7d7212e",
            "92460763-bd45-4166-ade7-132be982138b",
            "30db9439-6f4d-4436-8f7d-9202ded3ad83",
            "c03863e8-e7b2-4a62-8c94-870cebc1be4b",
            "2a09bff4-d405-46dc-943c-84bc33ee5244",
            "5d34f491-bdac-4876-8449-5715fdf6b566",
            "ea76e61b-1066-4ee3-8ecf-ef9824c61668",
            "1819ebd3-e366-44f4-b8f0-1bc890dbd2d6",
            "1407481c-9796-41e7-832e-e235ae4bda17",
            "5d25a14e-3610-4333-ad11-aff4eaabe050",
            "cf38e940-ba71-41f7-b318-7de232cd5dd9",
            "fced66d2-88d8-44fe-83b8-a7f4d2099dc3",
            "f5bb44cd-c798-4c15-a463-50aaf07e2f04",
            "7ac9468e-755c-4105-964c-8bfc947dcb16",
            "bbd2d4f2-18b0-4304-9193-381c2ddb3992",
            "f6bf39f3-c1a0-4970-a1df-01a95d480a1a",
            "39827746-69d0-45be-964e-d6b2baed94b9",
            "4b972f2a-e21f-48d0-8d80-89391700b2e5",
            "f457b168-88cb-401f-b846-2ffbf2cc59e2",
            "a550063b-e119-452c-9ee3-5728d9d8230e",
        ]
        self.mId = "7f7896dd-787e-4a0b-8675-e9e6fe93bb8f"
        self.vt = "AUTO_RICKSHAW"

    @task
    def location_updates(self):

        current_utc_time = datetime.datetime.utcnow()

        formatted_utc_time = current_utc_time.strftime('%Y-%m-%dT%H:%M:%SZ')

        token = random.choice(self.token)
        print(token)

        headers = {
            "Content-Type": "application/json",
            "token": token,
            "mId": self.mId,
            "vt": self.vt
        }

        locationData = [{
            "pt": {
                "lat": random.uniform(13.0, 16.5),
                "lon": random.uniform(75.0, 76.5)
            },
            "ts": formatted_utc_time,
            "acc": 1
        }]

        print(locationData, headers, "location data")

        with self.client.post(url="/ui/driver/location", json=locationData, headers=headers) as response:
            print(response.json(), "location results")
