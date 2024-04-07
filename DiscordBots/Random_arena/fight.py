#Класс бойцов выделен отдельно

import random
from base import MOB_CLASS


#Класс содержащий методы нанесения урона и поднятия уровня, а также параметры бойца:
class Fighter:
    def __init__ (self, id, name, clas, spell1, spell2, spell3, hp, dmg, lvl, age, xp):
        self.id = id 
        self.name = name
        self.clas = clas
        self.spells = [spell1, spell2, spell3]
        self.hpmax = hp
        self.dmg = dmg
        self.lvl = lvl
        self.age = age 
        self.xp = xp
        self.score = 0
        self.hp = self.hpmax

    #Метод который случайно выбирает то, какую способность будет применять персонаж
    def randspell (self):
        return random.choice(self.spells)

    #Метод который наносит урон противнику и возвращает его
    def usespell (self, target):
        maxdmg = self.dmg * 2
        mindmg = self.dmg // 2
        dealdmg = random.randint(mindmg, maxdmg) + self.lvl
        target.hp -= dealdmg  
        if target.hp <= 0: #Условие нужное для того чтобы исключить отрицательные показатели здоровья
            target.hp = 0
        return dealdmg 

    #Метод поднятия уровня персонажа    
    def lvlup (self, loser=None):
        if self.clas in MOB_CLASS:
            return
        #Условие которое даёт победителю больше опыта
        if loser:
            self.xp += 0.5 + loser.lvl / 10
        else:
            self.xp += 0.4
        #Проверяем достиг ли персонаж нового уровня
        if self.xp >= self.lvl:
            self.lvl += 1
            self.xp = 0
            self.hpmax += random.randint(20, 80) + self.lvl * 7  
            self.dmg += random.randint(10, 30) + self.lvl 
            return True 




