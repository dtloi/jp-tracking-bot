import discord

import rak_embed_maker
import rak_parse
import rak_request
import rak_updater
import update_last
import uuid
import pandas as pd
import datetime
import logging

from cassandra.query import ordered_dict_factory
from cassandra.cluster import Cluster
from discord.ext import commands, tasks

cluster = Cluster()
dt = datetime
log = logging

aliases = {
    "rak" : "rak",
    "rakuten" : "rak",
    "Rak": "rak",
    "Rakuten": "rak",
}

x = datetime.datetime.now()
filename = "log_"+x.strftime("%b_%d_%y")+".log"
logging.basicConfig(filename=filename, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logging.getLogger('cassandra').setLevel(logging.ERROR)
logging.getLogger('discord').setLevel(logging.ERROR)
logging = logging.getLogger(__name__)


class rakuten(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session = cluster.connect("discord")
        self.session.row_factory = ordered_dict_factory
        print(self.session)

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_rak.start()
        logging.info("Bot started")

    @commands.command(name='default', help='Responds with default channel')
    async def check_default(self, ctx):
        """
        Responds with default channel

        Parameters
        ------------
        """
        if self.check_default_helper(ctx) == False:
            await ctx.send("Please set a default channel with !set.")
            return False
        else:
            await ctx.send("default channel has been set.")
            return True
    def check_default_helper(self, ctx):
        default_check = self.session.prepare(
            """
            Select * from default_channel where guild_id = ?
            """)
        res = self.session.execute(default_check, [ctx.guild.id])
        for i,item in enumerate(list(res)):
            print(item)
            for key, value in item.items():
                return value
            #return "True"
        else:
            return False

    @commands.command(name='rak', help='Responds with lastest Rakuten listing')
    async def rakuten(self, ctx, *search):
        """
        Responds with lastest Rakuten listing

        Parameters
        ------------
        search: str
            Query
        """
        search = " ".join(search)
        req = rak_request.get(search)
        item = rak_parse.parse_item(req, 0)
        if item["item_name"] == "":
            logging.info("{} no listings found for {} on {}.".format(ctx.message.author.mention, search, "rakuten"))
            await ctx.send("{} no listings found for {} on {}.".format(ctx.message.author.mention, search, "rakuten"))
            return
        item_embed = rak_embed_maker.make(item)
        await ctx.send(embed=item_embed)

    @commands.command(name='website', help='Responds with list of available websites to track from')
    async def website(self, ctx):
        """
        Responds with list of available websites to track from

        Parameters
        ------------
        """
        embedVar = discord.Embed(title="Websites", description="websites that can be tracked", color=0x00ff00)
        embedVar.add_field(name="Rakuten (site code: rak)", value="https://www.rakuten.co.jp", inline=False)
        await ctx.send(embed=embedVar)

    @commands.command(name='upf', help='Force update Rakuten search query and responds with any new listings')
    async def force_update(self, ctx, *query):
        """
        Command that returns rakuten products that are new since last update

        Parameters
        ------------
        query: str
            Query
        """
        query = " ".join(query)
        check = self.session.prepare(
            """
            SELECT * FROM query WHERE user=?
            """)
        check_res = self.session.execute(check, [ctx.message.author.mention,])
        #print(list(check_res))
        df = pd.DataFrame(list(check_res))
        #print(query)
        items = []
        #print(df)
        # exists_check: used to see if the query is being tracked
        exists_check = False
        for index, row in df.iterrows():
            #print(row)
            if row["query"] == query:
                exists_check = True
                new_items = rak_updater.update(query, row["last_item"], 5)
                if not new_items:
                    continue
                # UPDATE LAST_ITEM
                update_last.update_last(row["id"], new_items[0]["item_url"], self.session)
                items += new_items
        if exists_check == False:
            logging.info("{} {} is not being tracked. Use !track to track this query.".format(ctx.message.author.mention, query))
            await ctx.send("{} {} is not being tracked. Use !track to track this query.".format(ctx.message.author.mention, query))
            return
        if items == []:
            logging.info("{} no new listings for {}.".format(ctx.message.author.mention, query))
            await ctx.send("{} no new listings for {}.".format(ctx.message.author.mention, query))
            return
        for item in items:
            item_embed = rak_embed_maker.make(item)
            await ctx.send(embed=item_embed)

    @commands.command(name="delete", help="delete a search query")
    async def delete_query(self, ctx, site: str, *query):
        """
        Command that tracks a rakuten query and updates every 15 minutes

        Parameters
        ------------
        query: str
            Query
        """
        query = " ".join(query)
        check = self.session.prepare(
            """
            SELECT * FROM query WHERE user=?
            """)
        if site not in aliases:
            logging.info("site code error")
            await ctx.send("site code error")
            return
        try:
            check_res = self.session.execute(check, [ctx.message.author.mention, ])
            df = pd.DataFrame(list(check_res))
            for i, row in df.iterrows():
                if row["site"] == site and row["query"] == query:
                    #FOUND
                    stmt = self.session.prepare(
                        """
                        delete from query where id=?
                        """)
                    self.session.execute(stmt, [row["id"]])
                    logging.info("{} stopped tracking {} on {}.".format(ctx.message.author.mention, query, site))
                    await ctx.send("{} stopped tracking {} on {}.".format(ctx.message.author.mention, query, site))
                    return
        except KeyError as e:
            # print('I got a KeyError - reason "%s"' % str(e))
            print("Key not found. user doesn't exist.")



    @commands.command(name="track", help="keep track of a search query")
    async def track_query(self, ctx, site:str, *query):
        """
        Command that tracks a rakuten query and updates every 15 minutes

        Parameters
        ------------
        query: str
            Query
        """
        query = " ".join(query)
        check = self.session.prepare(
        """
        SELECT * FROM query WHERE user=?
        """)
        if site not in aliases:
            logging.info("site code error")
            await ctx.send("site code error")
            return
        try:
            check_res = self.session.execute(check, [ctx.message.author.mention,])
            df = pd.DataFrame(list(check_res))
            for i, row in df.iterrows():
                if row["site"] == site and row["query"] == query:
                    logging.info("{} already tracking {} on {}.".format(ctx.message.author.mention, query, site))
                    await ctx.send("{} already tracking {} on {}.".format(ctx.message.author.mention, query, site))
                    return
        except KeyError as e:
            #print('I got a KeyError - reason "%s"' % str(e))
            print("Key not found. Query not being tracked, so add.")
        req = rak_request.get(query)
        item = rak_parse.parse_item(req, 0)
        if item["item_name"] == "":
            logging.info("{} no listings found for {} on {}.".format(ctx.message.author.mention, query, site))
            await ctx.send("{} no listings found for {} on {}.".format(ctx.message.author.mention, query, site))
            return
        stmt = self.session.prepare(
        """
        INSERT INTO query (id, query, site, user, last_item, user_id, update_date)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        """)
        results = self.session.execute(stmt, [uuid.uuid1(), query, site, ctx.message.author.mention, item["item_url"], ctx.author.id, update_last.unix_time_millis(datetime.datetime.now())])
        #print(results)
        logging.info("{} tracking {} on {}.".format(ctx.message.author.mention, query, site))
        await ctx.send("{} tracking {} on {}.".format(ctx.message.author.mention, query, site))


    @tasks.loop(minutes=1)
    async def update_rak(self):
        #check time to see if it should run
        x = datetime.datetime.now()
        #print(x.year)
        minute = x.strftime("%M")
        if int(minute) % 15 != 0:
            return
        else:
            logging.info("15 minute update")
        #get all queries
        check = self.session.prepare(
            """
            SELECT * FROM query
            """)
        check_res = self.session.execute(check)
        queries = pd.DataFrame(list(check_res))
        # loop through queries
        for index, row in queries.iterrows():
            #get the user that is tracking the query
            user = self.client.get_user(row["user_id"])
            if not user:
                # if user doesn't exist for whatever reason
                return
            #print(user.dm_channel)
            if not user.dm_channel:
                # if a dm channel doesn't exist with the user, create it
                await user.create_dm()
            # get new items
            items = rak_updater.update(row["query"], row["last_item"], 1)
            if not items:
                # no new items
                logging.info("no new listings for {}.".format(row["query"]))
                continue
            # update last_item
            update_last.update_last(row["id"], items[0]["item_url"], self.session)
            for item in items:
                # loop through all items and create cards
                item_embed = rak_embed_maker.make(item)
                await user.send(embed=item_embed)

def setup(client):
    client.add_cog(rakuten(client))