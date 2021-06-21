import discord
from codenames_game import *

class CodenamesBot(discord.Client):
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self))

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('&start game '):
            # if existing game, only current spymaster or ratmin can refresh
            role = message.guild.get_role([ROLE_ID])
            if (self.game.spymaster == None) or (self.game.spymaster == str(message.author)) or (role in message.author.roles):
                # check if valid game mode
                game_mode = message.content.split('&start game ')[1]
                if game_mode in ['easy', 'medium', 'hard']:
                    clues_per_mode = {'easy': 6, 'medium': 5, 'hard': 4}
                    self.game = CodenamesGame(clues_per_mode[game_mode])
                    await message.channel.send('Game started! Clear all nine cards within %d clues.\nSet yourself as spymaster with `&spymaster`.' %self.game.clues)
                    await message.channel.send(file=discord.File(self.game.board_image))
                else:
                    await message.channel.send('Invalid game mode.')
            else:
                await message.channel.send('A game is already running.')

        if message.content.startswith('&board'):
            await message.channel.send(file=discord.File(self.game.board_image))

        if message.content.startswith('&spymaster'):
            if self.game.spymaster == None:
                self.game.setSpymaster(str(message.author))
                await message.channel.send('Spymaster set: ' + self.game.spymaster + '. Clue format: `&clue place, 5`.')
                await message.author.send("These are your words: " + ', '.join(self.game.team_cards))
                await message.author.send("This is the death card: " + self.game.death_card)
            else:
                await message.channel.send('Spymaster already set: ' + self.game.spymaster)

        if message.content.startswith('&clue'):
            if self.game.clues > 0:
                if self.game.spymaster == str(message.author):
                    try:
                        guesses = int(message.content.split(', ')[1])
                        clue = message.content.split('&clue ')[1].split(',')[0]
                        self.game.giveClue(clue, guesses)
                        await message.channel.send('**Clue:** ' + self.game.clue + '\n**Guesses:** ' + str(self.game.guesses) + '\nPlayers can select cards with `&pick word`.')
                    except:
                        await message.channel.send('Invalid clue format. Example format: `&clue city, 3')
                else:
                    await message.channel.send("Hey! You're not the spymaster =|")

        if message.content.startswith('&pick'):
            if self.game.guesses > 0:
                picked_card = message.content.split('&pick ')[1]
                turn_result = self.game.pickCard(picked_card, str(message.author))
                turn_responses = {'unavailable': 'Card unavailable on the board.',
                               'death': 'OH NO. You picked the death card. Game over!',
                               'turn_continues': 'You found one! There are still %d guesses remaining this turn.' %(self.game.guesses),
                               'next_clue': 'Clue successfully decoded! This turn is complete.',
                               'correct_but_game_lost': 'GAME OVER. You lost. You found the right card...but there are no clues left.',
                               'turn_lost': "Oops! That wasn't your card! This turn has ended.",
                               'incorrect_and_game_lost': "GAME OVER. That wasn't your card, and you're outta turns."}
                await message.channel.send(turn_responses[turn_result])
                await message.channel.send(file=discord.File(self.game.board_image))
                if 'GAME OVER' in turn_responses[turn_result]:
                    self.game.gameOver()

        if message.content.startswith('&end game'):
            if (self.game.spymaster == str(message.author)) or (role in message.author.roles):
            await message.channel.send('Game ended.')
            self.game.gameOver()

        if message.content.startswith('&game stats'):
            if self.game.board != None:
                await message.channel.send("**Current clue:** " + str(self.game.clue) 
                    + "\n**Guesses remaining this turn:** " + str(self.game.guesses) 
                    + "\n**Past clues:** " + ', '.join(self.game.past_clues) 
                    + "\n**# clues remaining:** " + str(self.game.clues) 
                    + "\n**Mistakes:** " + str(self.game.errors)
                    + "\n**Total cards left:** " + str(self.game.cards_left))

        if message.content.startswith('&my stats'):
            await message.channel.send(return_stats(str(message.author)))

        if message.content.startswith('&help'):
            await message.channel.send("This is a rudimentary, single-spymaster Codenames bot. `&start game [easy/medium/hard]` to start a game; \
                `&game stats` to check the current game's progress. If you have questions or notice bugs, ping Maya.")

client = CodenamesBot()
client.run([KEY])
