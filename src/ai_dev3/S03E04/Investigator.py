from .ApiService import ApiService


class Investigator:
    def __init__(self, ignored_cities: list[str], peoples: list[str], wanted: str) -> None:
        self.api_service = ApiService()
        self.checked_cities = ignored_cities
        self.checked_peoples = []
        self.peoples = [people for people in peoples if people != wanted]
        self.wanted = wanted

    async def search(self) -> None | str:
        peoples_to_check = list(set(self.peoples) - set(self.checked_peoples))
        if len(peoples_to_check) == 0:
            return None
        for people in peoples_to_check:
            new_cities = await self.get_new_cities(people)
            for city in new_cities:
                new_peoples = await self.get_new_peoples_from_city(city)
                if self.wanted in new_peoples:
                    return city
                self.checked_cities.append(city)
                self.peoples.extend(new_peoples)
            self.checked_peoples.append(people)
        return await self.search()

    async def get_new_peoples_from_city(self, city: str) -> list[str]:
        peoples = await self.api_service.people_from(city)
        return [people for people in peoples if people not in self.checked_peoples]

    async def get_new_cities(self, people: str) -> list[str]:
        cities = await self.api_service.cities_visited_by(people)
        return [city for city in cities if city not in self.checked_cities]
