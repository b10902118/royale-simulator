## 檔案内容
1. arena.py
   - 定義了三個class：Arena，KingTower，PrincessTower
   - Arena()
     - self.place_card(Character,GridX,GridY,type="player" or "enemy"):放一個Character在地圖的第(GridX,GridY)格上面
     - self.update():更新一次，包含攻擊、移動，以及移除死亡卡片
     - self.update_screen(screen):更新一次游戲視窗的畫面
   - KingTower & PrincessTower 
     - self.attack(enemys):攻擊距離自己最近的敵方單位
     - self.draw():在游戲畫面上畫攻擊範圍以及代表塔的長方形
       
2. character.py
   - self.act(enemy_troops,player_troops,arena):此角色進行一次移動or攻擊or待機
   - self.find_target(enemy_troops):尋找離自己最近的可攻擊敵方單位，如果沒有則target為最近的敵方防禦塔
   - self.can_attack(target):敵方target是否進入攻擊範圍
   - self.attack(target,enemy_troops):攻擊target，如果是AOE攻擊則附近的敵方單位也會扣血
   - self.move(target):如果target在攻擊範圍外，往target移動
   - self.avoid_collisions(all_troop):避免自己和其他單位叠在一起，如果發生碰撞則會依照重量回推
   - self.draw(self, screen, show_act=False):
     1. 在螢幕上畫自己的血條、名字
     2. 在螢幕上畫角色大小(白色圈)，攻擊範圍(粉色圈)，視野範圍(綠色圈)
     3. 如果show_act，則會顯示目前角色執行的動作(移動、攻擊...)
        
3. eny.py
   - self.step():進行一次模擬，預設一次模擬時間為1/30秒(即fps=30)，目前是預設只出第一張手牌而已
   - self.render():呼叫arena.update_screen()進行地圖更新，以及呼叫game_window.draw_deck_ui()更新UI部分
     
4. player.py
   - self.deck:一個Character list，init值為要放在卡組裏的角色名字
   - self.elixir:聖水
   - self.type:"player" or "enemy"
   - self.put_card(which_card):要出四張裏的哪一張，如果聖水夠就會return要出的Character，反之return None
   - self.add_elixir(self,time=3):加聖水，預設每三秒加一滴
     
5. test.py
   - simlation_time=30 這裏可以換成你想要的模擬時間，預設模擬三十秒
     ```
     player=Player(deck=["Barbarians","Minions","Giant","Knight","MiniPekka","SpearGoblins","Bats","Wizard"],type="player")
     enemy=Player(deck=["BabyDragon","MinionHorde","Giant","Knight","MiniPekka","SpearGoblins","Bats","Wizard"],type="enemy")
     ```
   - 上面的卡組可以根據名字換，名字列表詳見card_img/{name}.webp
6. 目前還有一些特殊的動作沒弄，像是釋放傷害，死亡傷害，召喚，緩速，治療，巨石&飛斧&野蠻人滾筒的滾動攻擊，飛狗&石頭的死亡分裂


## Run simulation
```
python test.py
```
