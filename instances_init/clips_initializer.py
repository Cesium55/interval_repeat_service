from .BaseInitializer import BaseInitializer
import config
import httpx
from models import RepeatEntity
from functools import lru_cache


class ClipsInitializer(BaseInitializer):

    async def get_groups(self):
        http_async_client = httpx.AsyncClient()
        page_counter = 1
        data = []
        while True:
            response = await http_async_client.get(
                self.get_groups_url + f"?page={page_counter}"
            )
            response_json = response.json()
            
            # print(response_json)
            new_data = response_json.get("data")

            if not new_data:
                break

            data.extend(new_data)
            page_counter += 1

        print(f"MOVIES WAS GOT: {len(data)}")
        return data

    async def get_instances(self, entity: RepeatEntity):
        http_async_client = httpx.AsyncClient()
        data = []
        groups = await self.get_groups()
        
        for group_iter in groups:
            page_counter = 1
            current_url = (
                self.get_instances_by_group_id_url.format(group_iter.get("id"))
                + f"?page={page_counter}"
            )
            while True:
                print(f"requesting {current_url}")
                response = await http_async_client.get(current_url)
                response_json = response.json()

                new_data = response_json.get("data")
                if not new_data:
                    break
                
                data.extend(new_data)

                page_counter += 1

                current_url = (
                    self.get_instances_by_group_id_url.format(group_iter.get("id"))
                    + f"?page={page_counter}"
                )

        return data

    async def get_group_and_instances(self, group_id):
        http_async_client = httpx.AsyncClient()
        data = []
        page_counter = 1
        current_url = (
            self.get_instances_by_group_id_url.format(group_id) + f"?page={page_counter}"
        )
        while True:
            print(f"PC {page_counter}")
            print(f"requesting {current_url}")
            response = await http_async_client.get(current_url)
            response_json = response.json()
            new_data = response_json.get("data")

            if not new_data:
                break
            
            print(f"new DATA length {len(new_data)}")

            data.extend(new_data)
            page_counter += 1
            current_url = (
                self.get_instances_by_group_id_url.format(group_id)
                + f"?page={page_counter}"
            )

        return {"clips": data}


clips_initializer = ClipsInitializer(
    entity_name="clips",
    get_all_instances_url=config.CLIPS_SERVICE_URL + "/clips",
    get_groups_url=config.CLIPS_SERVICE_URL + "/videos",
    get_instances_by_group_id_url=config.CLIPS_SERVICE_URL + "/videos/{0}/clips",
    group_name_descriptor="title",
)
