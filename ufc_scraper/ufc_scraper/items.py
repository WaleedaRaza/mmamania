# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class FighterRanking(scrapy.Item):
    """UFC Fighter Ranking Item"""
    id = Field()
    division = Field()
    rank = Field()
    fighter_name = Field()
    record = Field()
    wins = Field()
    losses = Field()
    draws = Field()
    fighter_url = Field()
    rank_change = Field()
    is_champion = Field()
    scraped_at = Field()

class FighterProfile(scrapy.Item):
    """UFC Fighter Profile Item"""
    id = Field()
    name = Field()
    nickname = Field()
    record = Field()
    wins = Field()
    losses = Field()
    draws = Field()
    division = Field()
    height = Field()
    weight = Field()
    reach = Field()
    stance = Field()
    dob = Field()
    hometown = Field()
    team = Field()
    stats = Field()
    personal_info = Field()
    fight_history = Field()
    fighter_url = Field()
    scraped_at = Field()

class UFCEvent(scrapy.Item):
    """UFC Event Item"""
    id = Field()
    name = Field()
    date = Field()
    venue = Field()
    location = Field()
    main_card = Field()
    prelim_card = Field()
    event_url = Field()
    scraped_at = Field()

class UFCFight(scrapy.Item):
    """UFC Fight Item"""
    id = Field()
    event_id = Field()
    fighter1_name = Field()
    fighter2_name = Field()
    winner = Field()
    method = Field()
    round_num = Field()
    time = Field()
    weight_class = Field()
    is_main_event = Field()
    is_title_fight = Field()
    scraped_at = Field()
