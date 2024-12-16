# guides.py
# updated 16th december 2024

guide_eng = """```Guide to using Ludus ranking bot:

Introduction: Please write '/' to see all commands. Try any commands. They are quite self-explanatory after a bit trying.
The basic idea of this bot is that it is an easy to use ranking system for both clanwars and duels. 
Currently in native mod, clanwar results are often forgotten fast, but this bot offers commands to easily save and print scores:

1. Clans can gain ranking points and save their clanwar scores by using the '/reportclanwar' command.
Both clans must have an admin registered with the '/registeradmin' command so opponent clan admin confirms the score.
If you need password to register as admin, ask from Legion clan!
These clan scores can be printed with '/printclanwars <clanname>' or '/leaderboardclans'.

2. Admins can use the '/eventannounce <role>' command to message players about events. E.g '/eventannounce @everyone'.
The command sends a direct message to all players of a role. About 10% players cannot receive direct messages.
The command also makes a message to the channel it was used, and encourages ppl who participate click sword emoticon.

3. Players can use the '/reportft7' or "/challengeft7" to gain personal ranking points after duels.
These scores can be printed with '/leaderboardplayers' or '/printmyduels'.
If 'leaderboardplayers' is given a clanname, it will only print scores of players from a specific clan.
If 'printmyduels' is given an opponent name, it will print duels against this specific opponent.```
"""


guide_rus = """Руководство по использованию Ludus ranking bot:

Введение: Пожалуйста, напишите '/' чтобы увидеть все команды. Попробуйте любые команды. После небольшого использования они становятся довольно понятными.
Основная идея этого бота заключается в том, что это простая в использовании система ранжирования как для клановых войн, так и для дуэлей.
В настоящее время в native mod результаты клановых войн часто быстро забываются, но этот бот предлагает команды для легкого сохранения и печати результатов:

1. Кланы могут получать очки ранжирования и сохранять свои результаты клановых войн, используя команду '/reportclanwar'.
Оба клана должны иметь зарегистрированного администратора с помощью команды '/registeradmin', чтобы администратор противника подтвердил результат.
Если вам нужен пароль для регистрации в качестве администратора, спросите у клана Legion!
Эти результаты кланов могут быть напечатаны с помощью команд '/printclanwars <название клана>' или '/leaderboardclans'.

2. Администраторы могут использовать команду '/eventannounce <роль>' для отправки сообщений игрокам о событиях. Например, '/eventannounce @everyone'.
Команда отправляет личное сообщение всем игрокам роли. Около 10% игроков не могут получать личные сообщения.
Команда также создает сообщение в канале, где она была использована, и побуждает участников нажать на эмодзи меча.

3. Игроки могут использовать команды '/reportft7' или '/challengeft7' для получения личных очков ранжирования после дуэлей.
Эти результаты могут быть напечатаны с помощью команд '/leaderboardplayers' или '/printmyduels'.
Если 'leaderboardplayers' указано название клана, будут напечатаны только результаты игроков из этого клана.
Если 'printmyduels' указано имя противника, будут напечатаны дуэли против этого конкретного противника.
"""


guide_tr = """Ludus sıralama botunu kullanma rehberi:

Giriş: Tüm komutları görmek için lütfen '/' yazın. Herhangi bir komutu deneyin. Biraz denedikten sonra oldukça açıklayıcıdırlar.
Bu botun temel amacı, hem klan savaşları hem de düellolar için kullanımı kolay bir sıralama sistemi sunmaktır.
Şu anda native modda, klan savaşı sonuçları genellikle hızlıca unutuluyor, ancak bu bot skorları kolayca kaydetmek ve yazdırmak için komutlar sunar:

1. Klanlar, '/reportclanwar' komutunu kullanarak sıralama puanları kazanabilir ve klan savaşı skorlarını kaydedebilir.
Her iki klanın da skoru onaylamak için '/registeradmin' komutuyla kayıtlı bir yöneticisi olmalıdır.
Yönetici olarak kayıt olmak için şifreye ihtiyacınız varsa, Legion klanından isteyin!
Bu klan skorları '/printclanwars <klanadı>' veya '/leaderboardclans' komutlarıyla yazdırılabilir.

2. Yöneticiler, oyunculara etkinlikler hakkında mesaj göndermek için '/eventannounce <rol>' komutunu kullanabilir. Örneğin '/eventannounce @everyone'.
Komut, bir role ait tüm oyunculara doğrudan mesaj gönderir. Yaklaşık %10 oyuncu doğrudan mesaj alamaz.
Komut ayrıca kullanıldığı kanala bir mesaj gönderir ve katılan kişilerin kılıç emojisine tıklamalarını teşvik eder.

3. Oyuncular, düellolardan sonra kişisel sıralama puanları kazanmak için '/reportft7' veya '/challengeft7' komutlarını kullanabilir.
Bu skorlar '/leaderboardplayers' veya '/printmyduels' komutlarıyla yazdırılabilir.
Eğer 'leaderboardplayers' bir klan adı verilirse, sadece belirli bir klanın oyuncularının skorlarını yazdırır.
Eğer 'printmyduels' bir rakip adı verilirse, bu belirli rakibe karşı yapılan düelloları yazdırır.
"""
