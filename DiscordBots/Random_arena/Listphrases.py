#Здесь хранятся фразы для классов и функция по их случайному выбору
import random
from disnake.ext import commands
from disnake.ext import tasks
from disnake import ui

async def punch(channel, spell, attacking, defending, damage, clas):
  magephrases = (
      f"**__{attacking}__ мастерски применяет __{spell}__ на __{defending}__, нанося {damage} урона**",
      f"**Виртуозно используя __{spell}__, __{attacking}__ нападает на __{defending}__, причиняя {damage} урона**",
      f"**С оглушительной силой __{attacking}__ материализует __{spell}__ и направляет на __{defending}__, нанося {damage} урона**",
      f"**__{attacking}__ аккуратно произносит заклинание __{spell}__, заставляя __{defending}__ испытать {damage} урона**",
      f"**При использовании стихии __{spell}__, __{attacking}__ атакует __{defending}__, нанося {damage} урона**",
      f"**Магическая __{spell}__ от __{attacking}__ поражает __{defending}__, причиняя {damage} урона**",
      f"**С удивительной точностью __{attacking}__ применяет __{spell}__ на __{defending}__, нанося {damage} урона**",
      f"**Магический удар __{spell}__ от __{attacking}__ достигает __{defending}__, причиняя {damage} урона**",
      f"**__{defending}__ погружается в боль, когда __{attacking}__ направляет __{spell}__ на него, нанося {damage} урона**",
      f"**__{attacking}__ использовал свою волшебную силу, чтобы применить __{spell}__ на __{defending}__, нанося {damage} урона**",
      f"**Наложив на себя __{spell}__, __{attacking}__ атакует __{defending}__, нанося {damage} урона**",
      f"**Особо мощный __{spell}__ от __{attacking}__ попадает в __{defending}__, причиняя {damage} урона**",
      f"**__{attacking}__ устремляет волшебный __{spell}__ на __{defending}__, нанося {damage} урона**",
      f"**__{defending}__ чувствует силу __{spell}__, примененной __{attacking}__, и получает {damage} урона**",
      f"**__{attacking}__ использует магическое искусство __{spell}__ и направляет его на __{defending}__, нанося {damage} урона**",
      f"**Используя всю свою силу __{attacking}__ направляет __{spell}__ на __{defending}__, причиняя {damage} урона**",
      f"**__{defending}__ не может увернуться от атаки __{attacking}__, использующего __{spell}__, и получает {damage} урона**",
      f"**__{attacking}__ совершает заклинание __{spell}__, поражая __{defending}__ и нанося {damage} урона**",
      f"**Магический __{spell}__ от __{attacking}__ поражает __{defending}__, причиняя {damage} урона**",
      f"**__{attacking}__ выделяет свою магию, испуская __{spell}__, которая причиняет {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ мгновенно активирует __{spell}__, направляя его на __{defending}__ и нанося {damage} единиц урона**",
      f"**__{attacking}__ с особой грацией призывает __{spell}__, которая наносит {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ поглощает магию и воплощает ее в __{spell}__, поражая __{defending}__ и нанося {damage} единиц урона**",
      f"**__{attacking}__ метко применяет __{spell}__, заставляя __{defending}__ получить {damage} единиц урона**",
      f"**__{attacking}__ тщательно подбирает момент для использования __{spell}__, который причиняет {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ внезапно применяет магию __{spell}__, удивляя __{defending}__ и нанося {damage} единиц урона**",
      f"**__{attacking}__ атакует силой __{spell}__, которая причиняет {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ со всей силой произносит __{spell}__, нанося {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ использует __{spell}__ для атаки, причиняя {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ матереализует в воздухе __{spell}__, падающую вниз на __{defending}__ и наносит {damage} единиц урона**",
      f"**__{attacking}__ проводит своим пальцем по воздуху, вызывая __{spell}__, которая наносит {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ сосредотачивает всю свою энергию, выпуская __{spell}__, которая причиняет {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ резко направляет поток __{spell}__ , поражая __{defending}__ и нанося {damage} единиц урона**",
      f"**__{attacking}__ манит своей __{spell}__, которая ударяет __{defending}__ и причиняет {damage} единиц урона**",
      f"**__{attacking}__ волшебным образом вызывает __{spell}__, который причиняет {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ в мгновение ока активирует __{spell}__, ударяя __{defending}__ и нанося {damage} единиц урона**",
      f"**__{attacking}__ вызывает магическую __{spell}__, причиняя {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ применяет заклинание __{spell}__, заставляя __{defending}__ получить {damage} единиц урона**",
      f"**__{attacking}__ манипулирует магией и выпускает __{spell}__, который причиняет {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ с легкостью активирует __{spell}__, поражая __{defending}__ и нанося {damage} единиц урона**",
      f"**__{attacking}__ использует магическую силу __{spell}__, которая причиняет {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ излучает энергию в форме __{spell}__, падающая на __{defending}__ и нанося {damage} единиц урона**",
      f"**__{attacking}__ применяет свои магические способности, вызывая __{spell}__, которая причиняет {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ направляет магическую силу в __{spell}__, попадающую в __{defending}__ и нанося {damage} единиц урона**",
      f"**__{attacking}__ с мастерством применяет __{spell}__, удивляя __{defending}__ и причиняя {damage} единиц урона**",
      f"**__{attacking}__ мгновенно активирует __{spell}__, направляя ее на __{defending}__ и нанося {damage} единиц урона**",
      f"**__{attacking}__ вызывает нападение с помощью __{spell}__, причиняя {damage} единиц урона __{defending}__**",
      f"**__{attacking}__ освещает __{defending}__ магическим светом из __{spell}__, нанося {damage} урона**",
      f"**__{attacking}__ выстреливает концентрированным __{spell}__, пробивая __{defending}__, оставляя его без {damage} единиц здоровья и сокращая его жизнь на 5 секунд**",
      f"**При помощи __{spell}__, __{attacking}__ направляет магию на __{defending}__, нанося {damage} урона**",
      f"**__{spell}__ выходит из рук __{attacking}__ и попадает в __{defending}__, нанося {damage} урона**",
  )

  warriorphrases = (
      f"**__{attacking}__ метко взмахнул __{spell}__, нанеся {damage} урона {defending}**",
      f"**Бросившись в атаку, __{attacking}__ размахивает __{spell}__, задев __{defending}__ на {damage} урона**",
      f"**Мощным ударом __{attacking}__ обрушивает __{spell}__ на __{defending}__, причиняя {damage} урона**",
      f"**__{attacking}__ атакует, призывая силу __{spell}__, нанося {damage} урона {defending}**",
      f"**Величественным движением __{attacking}__ направляет __{spell}__ в сторону __{defending}__, нанося {damage} урона**",
      f"**Быстрым ударом __{attacking}__ сбивает __{defending}а__ с ног, и ударяет его своей __{spell}__ и нанеся {damage} урона**",
      f"**__{attacking}__ с удивительной ловкостью махнул __{spell}__, поражая __{defending}__ и нанося {damage} урона**",
      f"**Силовым ударом __{attacking}__ обрушивает __{spell}__ на __{defending}__, причиняя {damage} урона**",
      f"**__{attacking}__ атакует с неудержимой силой, использовав __{spell}__ как опору и нанеся {damage} урона __{defending}__**",
      f"**Широким взмахом __{attacking}__ направляет __{spell}__ на __{defending}__, нанося {damage} урона**",
      f"**__{attacking}__ с беспощадным ударом сбивает __{defending}__ с ног, применяя __{spell}__ и нанося {damage} урона**",
      f"**С неестественной мощью __{attacking}__ ударяет __{spell}__ по __{defending}__, причиняя {damage} урона**",
      f"**__{attacking}__ направляет __{spell}__ в нападении на __{defending}__, нанося {damage} урона**",
      f"**__{attacking}__ обрушивает свой __{spell}__ на __{defending}__, нанося {damage} урона**",
      f"**__{attacking}__ атакует с потрясающей силой, используя __{spell}__ и нанося {damage} урона __{defending}__**",
      f"**С легкостью __{attacking}__ метко машет __{spell}__, поражая __{defending}__ и нанося {damage} урона**",
      f"**Очень быстро __{attacking}__ направляет свой __{spell}__ на __{defending}__, который получает {damage} урона**",
      f"**__{attacking}__ с ошеломляющей мощью атакует, используя __{spell}__, и наносит {damage} урона __{defending}__**",
      f"**__{attacking}__ с мастерством использует свой __{spell}__ на __{defending}__, нанося {damage} урона**",
      f"**__{attacking}__ атакует с яростным огнём в глазах, использовав __{spell}__ и нанеся {damage} урона __{defending}__**",
      f"**Молниеносно реагируя __{attacking}__ махнул __{spell}__, поражая __{defending}__ и нанося {damage} урона**",
      f"**Острым взмахом своей __{spell}__, __{attacking}__ бьет по лицу __{defending}__, нанося {damage} урона**",
      f"**__{attacking}__ атакует с безумной силой, применяя __{spell}__ как оружие, и нанося {damage} урона __{defending}__**",
      f"**С ловким маневром __{attacking}__ ударяет __{spell}__ по __{defending}__, причиняя {damage} урона**",
      f"**__{attacking}__ атакует могучим ударом своей __{spell}__ и наносит {damage} урона __{defending}__**",
      f"**__{attacking}__ наполняется силой __{spell}__, и набрасывается на __{defending}а__ выбивая с него {damage} урона**",
      f"**__{attacking}__ бежит и кричит __{spell}__!!, сталкиваясь с __{defending}__ и сокрушая его на {damage} урона**",
      f"**__{spell}__ дарует невероятную силу __{attacking}__ и он бьет __{defending}__ со всей силы нанося {damage} урона**",
      f"**__{attacking}__ использует __{spell}__ в искусной атаке, нанося {damage} урона __{defending}__**",
      f"**С использованием __{spell}__ __{attacking}__ атакует __{defending}__, причиняя {damage} урона**",
      f"**__{attacking}__ совершает __{spell}__ вокруг себя, атакуя __{defending}__ и нанося {damage} урона**",
      f"**__{attacking}__ применяет __{spell}__ в ближнем бою, нанося {damage} урона __{defending}__**",
      f"**__{attacking}__ удачно использует свой __{spell}__, нанося {damage} урона __{defending}__**",
      f"**__{attacking}__ демонстрирует свои навыки в обращении с __{spell}__, атакуя __{defending}__ и нанося {damage} урона**",
      f"**__{attacking}__ совершает мощный, оглушительный, воздушный, двойной __{spell}__, нанося {damage} урона __{defending}__**"
  )
  assasinphrases = (
      f"**__{attacking}__ использует __{spell}__ для искусного удара в спину, нанося {damage} урона __{defending}__**",
      f"**С помощью __{spell}__ __{attacking}__ атакует __{defending}__, причиняя {damage} урона**",
      f"**__{attacking}__ мастерски использует __{spell}__ в атаке, нанося {damage} урона __{defending}__**",
      f"**__{attacking}__ чертовски хорошо владеет __{spell}__ и успешно атакует __{defending}__, нанося {damage} урона**",
      f"**__{attacking}__ демонстрирует свои навыки в обращении с __{spell}__, атакуя __{defending}__ и нанося {damage} урона**",
      f"**__{spell}__ выстроена __{defending}__ в виде ловушки, и когда __{attacking}__ приближается, она активируется, нанося {damage} урона**",
      f"**__{spell}__, установленная __{defending}__, ожидает своей жертвы, и когда __{attacking}__ подходит близко, она срабатывает, нанося {damage} урона**",
      f"**__{defending}__ не замечает __{spell}__, подставленную __{attacking}__, и становится жертвой ее активации, получая {damage} урона**",
      f"**__{defending}__ размещает __{spell}__ в скрытом месте, и когда __{attacking}__ проходит мимо, она активируется, нанося {damage} урона**",
      f"**__{spell}__, спрятанная __{attacking}__, запускается, когда __{defending}__ приближается, нанося {damage} урона**",
      f"**__{attacking}__ метает __{spell}__ в сторону __{defending}__, попадая точно в глаз и нанося {damage} урона**",
      f"**Метким броском __{attacking}__ кидает __{spell}__ в направлении __{defending}__, причиняя {damage} урона**",
      f"**__{attacking}__ смастерил __{spell}__ в качестве метательного оружия и бросает его в __{defending}__, нанося {damage} урона**",
      f"**Несколько __{spell}__ выпущеные __{attacking}__ летят в сторону __{defending}__, попадают и наносят {damage} урона**",
      f"**__{attacking}__ метко бросает __{spell}__ в направлении __{defending}__, пронзая его и нанося {damage} урона**",
      f"**__{attacking}__ наносит __{spell}__ на оружие, делая его ядовитым, и атакует __{defending}__, отравляя его на {damage} урона**",
      f"**С помощью __{spell}__, __{attacking}__ смазывает свое оружие, и когда __{spell}__ проникает в кровь __{defending}__ то наносит ему {damage} урона от __{spell}__**",
      f"**__{attacking}__ использует __{spell}__ для пропитки стрелы, стреляя в __{defending}__ и нанося ему {damage} урона от яда**",
      f"**__{defending}__ не замечает, как __{attacking}__ применяет __{spell}__ на оружие и атакует его, отравляя и нанося {damage} урона**",
      f"**__{attacking}__ бросает баночку с __{spell}__ в сторону __{defending}__, отравляя и нанося {damage} урона**",
      f"**__{attacking}__ незаметно подкрадывается к __{defending}__ и внезапно вонзает в него свой __{spell}__, нанося {damage} урона**",
      f"**Скрытно подкравшись к __{defending}__, __{attacking}__ бьет его своим __{spell}__ в спину, нанося {damage} урона**",
      f"**__{attacking}__ умело и скрытно подкрадывается сзади к __{defending}__ и внезапно достает __{spell}__, вид которого наносит {damage} урона**",
      f"**__{defending}__ неожиданно слышит \"__{spell}__\" со спины, когда __{attacking}__ подкрадывается сзади, нанося {damage} урона**",
      f"**__{attacking}__ тайно подкрадывается и атакует __{defending}__ сзади, используя свою __{spell}__ и нанося {damage} урона**",

  )

  if clas == "Маг" or "Моб_М":
    phrases = magephrases
  elif clas == "Воин" or "Моб_В":
    phrases = warriorphrases
  elif clas == "Убийца" or "Моб_А":
    phrases = assasinphrases     
  await channel.send(random.choice(phrases))    



