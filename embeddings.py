import os
import traceback

import aspose.words as aw
import chromadb
import pdfplumber
from chromadb.config import Settings
from aspose.words import (
    Document,
    NodeType,
    SaveFormat,
)
from docx import Document
from sentence_transformers import SentenceTransformer

import constants
from drive_downloader import get_header_data, find_document_id

all = {
'KickStart NFT':'1wuiqnvTUf--h9v6i_3cRGZCAXFYYo-PStfQzQ8utJUQ',
'Push Notifications':'1-o5xjTwG4w9tD01_2UhyK2adtmgyhGKpwPQErlqziIs',
'Additional Tools':'12GnetgVgF4Bmum0vh8qgxi7LUJNbGVKm284NbPJMGdE',
'Control Circles':'1zR0j_fHD8HBU5oC9fx0THAs26rc2yHzrs0XzCGfxqTc',
'Native':'1rlG0NnUe0HT5u8r2-4WKazTdWLnvn8QNRtycawh1_U0',
'Share':'1nFKhhYT0e16L1fLXveZvSEUUTIwWLUsVKCRYSTcdk-o',
'Spellbook':'1lNu-Gk9Ta5ZmogwwhTcUCzF3yhKPsmtatzAeWKyEQ0M',
'Surveys':'1DlhH5qpX9CPFn-G90sVoC1UzGHEToqVF_CatBR31ddA',
'Game Guide':'1rISMN9Pi6AlhMkN8w-zcPApi7-h4GEnkz8TkLCK57u8',
'Tutorial Flow Mockup':'1NnEprNRJUhikoImY0wVUZSZJAoG9dFU8YRzu7UidI0w',
'Face Swap':'189oA71sTALj6YXA3MnR270Ni6FYZ4IXJfLTZ2Pu4HHQ',
'Giving Works':'1u2LJ8ZAnIhXtXGTWw76OrGQv4HgRB__4z0wHlRAO4MY',
'Campaign Map':'1hn7QcmzYtUg1cFdH3kGJz3IW3CKUHLfPsWxS-cSbewA',
'Summon':'1HDaBnlpR4Mu-ryXb76Q4LgZpRNaqk3EX5OLacZygNqc',
'Quests':'1Np2Gp76TY8neXCeiMtSU4Gs3cXr_LpVmUA9zUND5a0w',
'Jackpot':'1oEcC_iRPaH7T0MYk6VAF5ogm5zbkUMfS-SMw5wpExVU',
'Avatar':'1JEMG9x2a-3usggScArfbE0Yl2LDAqF0-ACi3FkqwFK0',
'Crypton Mine':'1ObzTWsVdpQ9oPy2oPWlz-i066hMrO1DaLPDqQpDU_4E',
'Settings':'1uT7GIRrUyR9cQxIIWhhlDrSqa38qWkhlTkgk2rErExY',
'Black Market':'1GmnRx4sy2B8QwC5y-dweNRu8P9n-FzhfraBrnuNgbeg',
'Unlock Upgrades':'1nulo13ziWKYOLRQQABegZJv_z-aHoQbR-4GmGxczCbE',
'Support Building':'1NHmSALsowq6uMB0mClY9zQ2nTBvfL6EvfjBcOt4zqpY',
'Gem Mine':'1RK4HYZ1rHYutb2IIk66lX0tNpsc8h_3ut8fosAhD3CE',
'Campaign Tower':'1GVFPivrq9UMHpvsaR34sqCmaN9D2GjWNQNeL98WYahs',
'Special Deals 2':'1cddk-AKc3ZBHZd2GXKpinFgTfyr5U5F_JQmUV9wrK8c',
'Marketplace':'1E8FDEuI62skJzS1sPmnpcetG9jh1FrKb8qPh5XNhusM',
'Special Deals 3':'1qepZ3HOrugwjgeu4XtG6nddPVBpokahCfgMFrlgJ3VU',
'Copy of Collection':'1X4RK0qIUFuLjSq8ovPyysDr9cmYFCFl9zgz3Q9Dja-k',
'Special Deals 4':'1QmycA62c0DPcPYslpgecKLRDdqtMcCWpQAxsQVS0ni0',
'Geopet Go':'1Sdx_J7TqSnRatY-9gqwyGqOMJjPCA2iD7mH6IZVISKs',
'Mailbox':'1dmhmvWvvHqwHYQ6f1NBtrpe2fS9jaSkpr_Z2AxFXf4A',
'Special Deals 1':'1oXOSh6G4mBWtq5D4uqfpShSJmsVAmYSsapiOEJfGZdo',
'Seasonal Challenge':'1-glKAxMPbLULOjw5FGR1QWOg-uS8l9nNocYX-oY0Z8w',
'Achievements General':'1ZBTjZa-0RlXyk0ESATyu64-gPh_J_Iia04QEgK5moN4',
'Crypto Land Outdated':'1Of5WsKvEb8Y-pLNCkGFCJ0pukjxx1wsPmtGEQXygBo8',
'Community':'1YD8IYH1tO50WL-GSfY95tiTW2PDjxhU6YVj-7Wj3Z3o',
'Auction House':'1vG1ia2MokGgykqBdEj9SU5a5kSvxXOyV8SaaBWJiYgM',
'PvP Simulations':'1Dlv_Wqxezw78zGUbG7-oAn9cYHp4BSUX9RafsJRa8kM',
'Collection':'1S3CzIG8Lt9KcysHNUFqy5qHv7LVuIEOuvso4HC2Hmx8',
'Main Menu':'1V3WYDgSgHhhUjOEFCu9-lR1mTqN5kmD5398DD8UtrmI',
'Arena':'1a2MNvGcqmIm2dLGCvrNyCGUUWSOEf_0RCc2RPWsG8lY',
'Shop':'1x2UOudZ5GQcnNWJl3TMHRwA7ZEe0nNuO9hYqVcSu-eg',
'Trivia':'1iw3JjxrSCiG6flDNw2Fy0jIcCCIyMFYXhEWzi_DeXPM',
'Pet Guardian Building':'1gnpXwMQzM7ukiBK1gd6WE4_65oA6BQxsa_pzwt_eIP0',
'Villain Challenge':'1BfarolL6DuxzQwONXvXHhK7yfeJPuqkSYRRZ0h1ljZE',
'Achievements Building':'1fuYhnlKIFHDtdij2Ow7XWjnBKizsrw_5-hTa_8EOw_E',
'Community Browse':'1JmEtMHX23QVl8n1rWXuhsNuNdyp1Ma6QR_kasSGiyzI',
'Idle Boss':'1h_KpOv2tn6NnGgRSjuHAEIHib8YwjrwhHp3usIUBR-M',
'Mini TTTT Challenge':'11vigNDme7SMOv2hB4woYxtY_9TfZmudoddP91ZiVXr0',
'Treats':'1IAnqARVEZDPGFEWbjjdU1h39EzhCu2NLt9roH--ZmIQ',
'Upgrade Building Pets':'17ahg4kpu7mUythakUrab-Td0z_3UjgNzsWxdnFFPOVg',
'Stories Post Types':'1kdO6i3Iee4_gUWgWy3uXOy6JJ18lnAGw-UcPByRbpxg',
'Stories Twitter':'1VFcrdw8hljti0gcTf5aIDS4ylFQi756QY_Ts4VRTvjs',
'Stories Threads':'12YpTJUMbWnCX14LBZgHuxGlJo5DoV3KD__7_Ar9S9zI',
'Stories Forum':'1EV-NDxb_XenUQY65cKeIOIubznutr7DHuLy3_K5Xrrc',
'Table of Building Pets':'1sYy_fN8V-ZVaUOhGBReUppUv6B6x0Uqc6Pr6ntarl6Y',
'Customize':'1ZItOhrR6EXTWdV1iCg4rtawyXXoDDNCFREFAQnxwHdA',
'Match3 Game Board':'15WkyIO49Hvbo7VGQwmLxnrTybvEzIFtDGOn3U86NK24',
'Match3 LevelCreator':'1v3fMpbAshKWWvSwc_LsvhsvjUDsb1sIwd6ptTDQSGEc',
'Match3 Player Created Levels':'1x8ORjx4MoWpmxi4dGHdEriGLxRq2eorQTK6cMKZiDT0',
'Match3 SelectionScreen':'14-ES5ftHdOove9kY-kXZZTWGt2e0qMzLNU3WX33VKKM',
'Match3 GameRules':'1iDNn8l5czIbjDP6HHRsP0pZtD9w-yyhQqizYfayVfrA',
'Chat Whispers':'1_75h7a3lzlBUPOJgxEV4b0ICudAmhetaeEjGLI0coBQ',
'Automated Whispers':'1k1spfTvYe5OsSJ8KY9YChSt82ve8HXB-9cJ8nkSNL_0',
'Chat Voice':'1vM21lTCPKzjmTkl3k1ks2b5egfRVSOcvZ1fVzp2TkGc',
'Chat Text':'1ru-QSPOaPklPKTxSaWUW9LHnlLHaaIX2dxSoNauwYkk',
'Chat General':'1Xf0zDiGhb09pM512XGGUVhFtuSyKdpoVsrK79-5hNzo',
'Chat Servers':'15faytzoWHKzzPC7QtOo3y3PeTJ3fiPUE-c7ocqyeGts',
'Chat Media':'19l5AKrRX2SYZrPY2ST_TvQyz-2t4hw8AglIe68wRGaM',
'Chat Notifications':'1xTOYTTpE0AB8OX-zIXedA8g0fPUHu7PZxAnMzF2FxBQ',
'Poker':'1Rmi2OsB9EVMQxlP9fMJSFHdebJrsXaf5BLNDRr5clQk',
'Bingo':'1wd3xkcOxh9TJkcoe6yyccvXca2SzoVZrJ1kp1l1q13M',
'Table Games':'1C-b4QWiKDCQSbbQMqYXMTiLyIl3ZSJPWno4IeaAV5Fc',
'Blackjack':'1Y05Dezg5H4oszZ6fDXjCzrqZo8MpJtXN6kcpVC9WjHw',
'Roulette':'1gkLo-P8pvh1DavGIy__4loNynrSKGgfgr44xKvMzB1c',
'Bootcamp':'173oeBLpifp5dgIRhzZgmVBjcF1pgltbu5ZAXt-eO3_4',
'Blockchain General':'1e2cbzEKXH0gjd0wZPRQflIf686AjiTkPpG8A3-uAcvM',
'Crypto Land Lore':'15e00LJFpcO_WqlzBwBw5KliAUclElwXlhA5dNkA8Kts',
'Blockchain CryptoAH':'1DKWoZFXJWR5at3G2ZMXoYQzEglDzdTaa7HUMAvDdyuk',
'Crypto Land':'1r9uhnQyQ15yA0VuJTDhnCO27BLbz5_cHFT-KNLgyOdI',
'Blockchain CryptoActions':'1pRewgJ7nDKl13Yz5W1efVGbVU5HNAif4usezxWul03I',
'Live Streaming':'1u1Feq7YorwwQFScFhweYlGgNonoPdRSN484-wDFBCtA',
'Table of Go Live Alert Toggles':'1vSLNwyY2NRfRbIrlMtoaGF0Lb3r-QzWZ7wZ8zmUSVrA',
'Go Live':'1pAR0uUbHssfCc3asLVmjZJ-qZHKOyXAvWyS2GOtg-j4',
'Replay Book':'1Btq5EtyWEN97VjD8pTmAnNBIvx14K8oYKvBggVEKuZ8',
'Replays':'148oAW2Ogosk5OCP2J2o9xtIVrpgeS2c-cm11eSrxokQ',
'Changes to the book (only chapter 9)':'1ATO9cNwcKNI3zteW8a13eiXUxe4LZ-ehQ-K9SQ67Y_Y',
'Church':'1TcIHo3hkkrYmR40jUvtXOKPrxVVVlXKQv3CBQZpcNRs',
'church the real book':'1oMj3iGOBtBCXRrZloeCiBpQ8lC6HkgbhJ95Y3DPgUbI',
'Weekly Events':'1L9co2LqK4TBMK9NFWaxOBcG06OqyterVek1c1ZXQHQ8',
'Special Events':'1AuWg82LE-t6ZMqnEqQmA2VSy_3zdHdU7WB9ImvP4BuU',
'Permissions':'14kHn3xtIZvMjxd-9Lq4vHwdsg5QsZYaPmaAhgIG3xGs',
'Admin Client Custom Mails':'1iOpDEpSpaxkfYEeUKl8T9obdLw5s3GTk8X-7eO3LqE0',
'Admin Client Moderation':'1aNERxc7F1jAiTvDXiWDRySFa_M4jxVIV5GvBP2Up4b8',
'Admin Client Profiles':'1qXyQVe-vJafftWAqD2cNe-rGHTWnm3yY5R4BjNSptZI',
'Admin Client Log History':'1-gTNJC6D1qsEfm9r9YFLUGzRNozu8XZd0-Ji3UO7gno',
'Admin Client Calendar':'16nT77D82Ul_B_ExFitiKU33Sd-rmh7OrOJw1WSwqxW4',
'Admin Client Tabs':'1M1lq-E_8Fly93TziQRHOQVSl6iGceNO8acNSN_93Sh4',
'Admin Client General':'1AF-G-IKWSQ_QSFwUaLu_xIpBuNXGEIYt8IFYwY01oy8',
'Pets Post Launch':'1eVEVOFcrbzKmAGnITsQ9OnTqINBDmaUPh4rzEtXP7Bg',
'Push Notification POST LAUNCH':'1fFgLcT0xBIOKcoYkkUQzD9sP8zCZoJm-nMlEIOskH2s',
'Chat Media Post Launch':'1tJEB9xfDEBxPvNWGBpWCIhznZwm0_kYLj5GCLF7Y6bk',
'Settings Post Launch':'1bAFEO4ccfanPohdolOyu7mqYh1dhl-1kprQ1r06FWaI',
'Garrison Post Launch':'1tydin0KJAoXzQq5Kh7hRXBgnK0w96RcihrXngR_xoEs',
'Share Post Launch':'1swrhXiqY6Zi3SrWIH0uwkg6fznLW63lLKLKFqUsmfX0',
'Community Post Launch':'1IHt0q4AOunFPbRpfhH2CFgNwP66G4Syq7XX5MzVsmTM',
'Game Guide Post Launch':'104gIU6wxRyoYL2pbHff8NDO8DuWe7xnVmv8AOaM1hno',
'Congrats General Post Launch':'1etW8bKR7tmxUD2eSBPju2oPBDTHjnjXCdzJiuMwRm0Q',
'Native Post Launch':'1IpuskOHL7xzfVaxaxFlzVy2nlcyVA1cS5m2CdlAIzZY',
'Stories Post Launch':'124hBRLl0EvXCu7ZfUH6TihcqYHambbpYr6CnVOXrpFU',
'Marketplace Post Launch':'1G2ZpKA3vluCH0goDqNW6MHNMk-M4O5UgduW3doOeo-0',
'EventQueue Post Launch':'1V1yfwETYwaBhdsICduCe-b4evpR5AK4nywhscEUpYpk',
'Replay Book Post Launch':'1lgpsAdBG_4h_Y-dOv30HPkWnl4yRiFxQBdvIG8DZ3-E',
'Challenges Post Launch':'1GSKFe3_qih2xbzVvWfp6iKdTmsg4JPfhs3jYbNtYHC4',
'Future Post Launch':'1g6n-66MVRhtqRw4CwsuC-FueKbN8APoP_n7P-oo1AAg',
'Special Deals 3 Post Launch':'1VUVierY1kt3B00mpw9biIp-FhtxnPB68wa_dMA5510g',
'Modals Post Launch':'1cUgQxe1rkAOquoa_7HDNJLhmUos4K45jJMkoLSsOmHg',
'Auction House Post Launch':'1we8MHLL2qUlW4E6Flnt2_DqgOW6I9qlnafpOJ-0HtmQ',
'Raid Post Launch':'1hDewimpJY__c8HQPgSzOV8P_H5KDZXEb-yvPyin9ig8',
'Stories Forum Post Launch':'1iGgsV0h_M7-PdvKBnd9pU_5ojjeXvAlaJFtqiUkTPeE',
'Chat General Post Launch':'1nsvQzmHjVPaAqfShPk_HaEOuwB6G5d4sk12PzQht8tU',
'Community Browse Post Launch':'1SPIsmWECmTgXgC2DtoI_hFpzuWmYbB3E1RRpXI2885A',
'Special Deals 2 Post Launch':'1ufetnXuc5BFCbYhobpFMHD5rP8c6FZFYeWgdbomMTfI',
'Chat Text Post Launch':'1c1vKb9m__wLMU8Oljm2UAdrhJfYNDnV8v3y9L4mHvhY',
'Weekly Events Post Launch':'1ceCyo2JRCYby5nlNDIF5dLaPSBXsS-dyxJufm3A9Bgc',
'Avatar Post Launch':'13DgyDwYGDkY-sZezMXwl1_RGO5JHhc00W5TdJxNUbIc',
'Chat Servers Post Launch':'1Quids2HyoxCiy6nCNpRQGBdXZrSM5c5yx_fe0UvjnWM',
'Chat Voice Post Launch':'190aq3rYA6c3mLHZhrcGUTbY2jeewJfx2Mbx5Rs3omKY',
'Mailbox Post Launch':'1_R5oA51ywB1d1HqFrRVcK8IflauX7K3LeBPX53GMtBU',
'Spellbook Post Launch':'1aA4S3_Gav9TJcQmj0gY4cGV9cy_dfoheDVmO6wXZ0Fw',
'Collectibles Post Launch':'1FvejVsQR8nqm6UjZ-GGzugi8iqGh11oRL-Jyacq9NUI',
'Campaign Post Launch':'1_ieJTcnK6OIW97y6bch0oQK13BQPnBj9sjNwyOCWZoo',
'Skins Post Launch':'1HrxJyx4blckJ_aF-ttzX_yFToYz9TPjR0mFHo1GSBmA',
'Media Player Post Launch':'1cqpgfgFcDalVlEAaqv62cCpXWnixZiUGFeZVi7SKJng',
'Stories Twitter Post Launch':'1TNPQtbdtYkl5l_xquA0ivKpS44NQpD6pXiz7Z0GsIcQ',
'Replays Post Launch':'1Hzz697L9yY1ga6pQPWfs6hD5ptBXZBTagnhAtEMCoz0',
'Stories Post Types Post Launch':'1zLs0GUrdDOPuUiMOP302ChPF6aHOmyMNAsTu5kuXT9Y',
'Daily Quests Post-Launch':'1QHGsCFwKHecc6XV8rMUxwQeh773uGyQNHRYZroex60g',
'Special Deals 1 Post Launch':'1E-1cp3rLaDvmb35sc7kgZ-mlaFJdKPUEeKNUmmZDsp4',
'Content Pieces Post Launch':'1rZ2_Kla0Jc0JkkxDS1dVIdx3CSuiCZxH-HBLZ6bk6lg',
'General Events':'1oQ6PuPeZpN1OOqN1UjJvtGCLcFQz9sZNOe8N69TEvzk',
'Chat Notifications Post Launch':'17OD4Txyz9G-zKF0pv0u-U0Lzp25-CgmysezFizbtJAA',
'Collection Post Launch':'13p99UerPjX09z6h2rOGOCS1rv2j7JX4rl5NWYz8U9Po',
'Accounts Post Launch':'1zrJKsSVBv0kB0h-oZY9LDo-ZU5BEXESkB7qqipnmkrc',
'Video Guides Post Launch':'1EGzJZX9E3LyKA7nlz_iXYdLK2umUA6rwJ8h1FoU9t0w',
'Go Live Post Launch':'1O0WT1NxgY7lnEaetfvNX10PYy3UnUwMXH6T4IbJcyhg',
'Table of Fighting Backgrounds':'1-n63jpa5pM85L2Z_fRA70jUFut0h_lA3FcpG7zKDB64',
'Tutorial Audience Retention Design Test (delete me)':'1TZFb345xaTqQ-bl_JitJa8rnpj7kXYnt8odCDTVhp5w',
'generic lore sentences':'1LD6sVlghSTaiAsSdP9qtPK0otdpk2c4DSRNEPH9wRRQ',
'BETA Outdated':'1og3Q_RvwN7bDU5IZ3vs6lMGXVmUYpSV0ud11jMtbKcA',
'Prefab list':'1LXmgJvp_PpvjYj4v_FoHUn8lLRe2Ew96TIR_vWhy690',
'Smart Buy Achievement Progress Bars':'1oezTKEAgVBmtkGfdKitnBSi8RJfIKPpnhKClkkICnxo',
'Push Notification Brainstorm':'18aLEsWuIZj6eh9fwF7NPJANpQKBIwdBhT9cNXXOZO2s',
'Test':'1VxpAvSHeNz-2MrImh6MburztOlyG7Xw4KS-GD_BCBTs',
'CoS FAQ':'1gejiB0V1l2ixm17CMwpRu5pXXu76-9-yYUG3XiwMmho',
'Copy of Test':'1L6_3CjUw0YOagO49XsjyY40yhOOU7EHWxR46hlYVgrI',
'Bidstack':'1W_A2qfQVLo20AMMvcNE0Q0c5jGbXXgjCKidbOz2aGT8',
'iOS Resolution Center Replies':'1NcviSgV6AIqE9_VxAJPvV-C5ewb3dbI5ud3EhuAsV-o',
'Writer Templates':'1T5rkh9QF3CmAQ1NnDSZNJdNwy1FNUEI3fYi-mEC6TN4',
'Pin Game':'19GUWZPPHybAxXVkUPcF_yddXS80jp5H-n_gnFYx9TkQ',
'BETA':'1FKpymHpu6zpzOuFFRm-xNteEmIDNf0qWl_yAGjg-NX8',
'QA Video Guidelines':'1gCsW-BWYC1T5SWpAJrAXGvk4trgUm8ES7-s18Jwu4tE',
'Subscriptions':'1cTIe1lsosqzFm6PmZQEmUJY9HA_JKxn2Ktz3v408YIg',
'Sale Points':'1Wn0_eZ-fnV2ovO3FKKVQkz4ao2vn99OlPSuPNdnz3ro',
'Presents':'1brUpF44emFCldn7JdCY5yfglZlZILMtUy1s91MVrezM',
'Consumables':'1U9zajt3iWMSzTRVu1A6s2fBz-fUNzmsxTXk1X_u6cbs',
'G4G Shop Limit Texts':'1SB-D-U54MHJCh99rsnZFWeZnQ3sB_lUnArTvEGQ7-2k',
'Topup':'11QF2M5x9oDPgwqRktyf_IoiRg0zN52qGBNrjzqDKFvc',
'Purchases':'1HUfVmcvegzCDggNIUqbhbRMH55kmDVDQUbdcA1K9zx0',
'SocialLogin':'1R6d56Um2AiiiZ27-3jIKM4AtHUMF4omB-RsGzFDlXdI',
'Accounts':'1eGbgzJYn2x2I07wDLgLFxxaZYYPJ6lvCnx1LZiBUESU',
'Trust':'11kKxD5AJk8SxkG1RqmKqajTTB6VlJYHlO29A-1Sh8_c',
'Security':'1d--PalXkfsYWtksoSsYZl3PW9rZQtC5AM53oYiqphlg',
'Data':'1Cgzx5C1ERYC-Eo_LTmQ2QRYH7WSE6S8FySXKKPh8lxQ',
'App Store Connect - App Events':'1hVxW7_qGQGlBDaGA5HnFLRCLZm2ZCsA-DweUU4EgFRc',
'MoMi Whispers Retention':'1Y-vcLHHw6Fgw-GKsRPfEmlIxNboV6O3Sm5Y58YRXcwg',
'Automated Messages':'1Ypqer1SVjC0B-s1cjM7qF_s32NMYte-Ft1dP3ii1sbc',
'G4G Shop Purchases':'1hhd97hzw0VC2UMRUtIELPCr91_3V3FzCq6S4D-dS0OA',
'G4G Shop Pages':'1bIZNvIwTo2Dh2tZAXXsacHkuZPrRLCX1nQfpJ0s1_UE',
'G4G - CoS BETA Features':'1qXG97W095Xolx-1Z3BzCaJ95MA7MZsN17ajjgKntdCs',
'G4G Shop Checkout':'1-x8QNgwtkD0QPAtisCF06kjxTsqYHq2TbaqkhgO7RTI',
'G4G General':'1lacFb4yDLWKmxLD-V3px5WS8sMvV-_1gGsof6R6QOgY',
'G4G CoS Integration Dashboard':'1dQMmKUn-lZMWPqXFhr6WVI3mGA5X-sytfF98idvr1pM',
'Faction Stars':'1C8BTRJ0xtiSZX2kCnEXyYj4YASofvRc9DAOJKEaIsFg',
'Loot Cards':'1h6DO5_Kd7hkd7yw2sNx_qHFxrQsS71rF9hao-fwm6D8',
'Stickers':'1athLvuSL3rGMMm-xSa_Ue--RTKFsWbNHOZjcovl6Fj0',
'Pets':'1RGF5th6ff9gH30L87UUgRLD2gxkvnvJ4qBGFplX0ImA',
'Collectibles':'19MELcTfYWrr9FbVjxkH6LS8heIPml8BXClDPJin09CQ',
'Pets Categorized By Evolution':'1mK708n7TOBUjygdg-mbv8VeiQ0SqHzszxVs1EvwXSAY',
'Skins':'1xIZGyz6akoyUgP72pvCiX_HBGUET06EcgT-fKxQHxSA',
'Heroes':'1rhve2TaHirJXC4FbtWg_bR7d0r_-ARckh67S9ayOyrU',
'Guidelines for Face Approval':'1qWesA0-i-1tYOC4XkZns0oremiOWVQmdDBFhsFpcodw',
'YouTube Integration':'1zaAs8uz98QTEcY5GS5mjYdGQNfiBFpZ49v5dF8PNGlw',
'General Info':'1ZtTxL1ImwnsztuzdaDgRwn10yyCnqlho-vnLTGrAPiI',
'Lore':'1f_Yjduzv3xFtCsXnFUJToRdHuY81Gvolb4Bd--VRc_w',
'Catchup Luck':'1nM6BXFWQHs93Fa2wrgiRJuwLN3ae4S1B5SW7Y9Phqeo',
'Roads':'1AIeHt3Q3HlwHGpc0AMqsraoxg33-5bjFp66MfkeSJVU',
'Future':'1BA3weYSZ6WlBHLsIOmELtQSHC-jzb87tESSpEdnWON8',
'Content Pieces':'1Qs78YcB7Gybop0daMKDt-y9lzJz8_3WH-sKk6mtFzyY',
'Visit':'1ZiRjxwGgquan7dKFcxdvXJ8ghbMel_28teCiBQM-4no',
'EventQueue':'1bQA_ru2dH7kuLvmdQBPWF3V9oAHOIu6iJorH0XYMzLo',
'Challenges':'1D1SC9u8NS2YUFtlK0HNTjIONsP13QZJqTUafpnAozBM',
'Mini Alerts':'12mMYZtil63fVETqhFzxEjJ5u-KBoStRh7R22MOS5HxY',
'Gift Crypton':'1Dc4h2Gcz8Kjj7HeovPgrGnBaB2putdktWbwrcf-_O7Y',
'Lists':'1qe9QCqUZ6BhhsAwpjTT9qG9xoQxaY2rsa8_CnmTZMGY',
'Game Startup Document':'1MN3xDFNqojeNjxcUKISpCrwTiuPdZUo0TVPb82uI4HI',
'Selfie OUTDATED':'14jQarB7vddDRTElAST7ySvkvWHzOT_ly9uzqOWsGpZg',
'Input':'1_wQrAl3pSHnHTR8s32fEqeG3BuRFLUzF6ZZU_qtteg8',
'Media Player':'1yHrrt5jYPKERe9rBzt37j5axKI8zgtGdNffH9x9AXNg',
'Merge':'1JGMYkReRqGsdlEB6wP4rfUbMpb54OUhhgc3fo-6FiHk',
'Players':'1ir_s8t_0osx9kKHxBBwvINdVRWS4gwUOCvMTQeqUq5w',
'Top Bar':'1daWFN2e12jXeH-eLhRFsxIluf0oFRsAWGBifi1ALUb8',
'Visuals':'1goDGIfBWoEKKDXNK7-VlCazdYf-8d9Vf5HPG4FjSuDo',
'Opensea NFT Flavor texts':'1DewacI-NTxxdptVsB9E7J3r0sXjInzomb-YFXtY9wDw',
'State Priority API':'1YwlWIGgPbVEPZ1zflriZDITiV9LhEHqSuRPMpwY3A3o',
'Banner Messages':'1x6A4-o2yP-tugoDIDvH47N4OYh5I0H2fEHOqdypZVBg',
'Fighting':'1lbp2VGYA5lI8oft_HNp5TU5uelozqnpxsCgnZQnWFXM',
'Selfie':'1aD4nMROlLaMI04xnT8Ei2vRfCWZP8GjAdhFBWRf25WE',
'Hidden Secrets':'1i_XX988s080k6AFcvzlzXNzFOBZJO2iQva4UvlZ_eBA',
'MiniGame Tutorial':'1FLZp_DHN7o5QEyqBnWeP_LeBKZav4ElzgcX4-sig9Nc',
'Tutorial Sequences (delete me)':'1flPBcduFyHUV51rn46HitqTnUvaGu0nRY0xGuq37toM',
'Mission Sequences':'1hPZNn7son2TqQEJIIgX0Tp6QL9dCOCbRvICQ9jr7uV0',
'Other Leaderboards':'1X13RdPiJv34o_piS7bb6V67fxv0tjRqWzLvfblNZVD0',
'Division Leaderboards':'1TQriDfQ5b8dmaM5Ue3s7QY4i7VMDofIzwAkC9mLHdVs',
'Table of Division Badges':'15oqP_hIg0fMVITzlrkQCbJsT-9gt4ZQR_ksNFdh2pY8',
'General Leaderboards':'1ypjqG9FOqsNG8zq5rMJLtHhoqqDP-60UlSzX2UBGK8s',
'Congrats General':'1ooLuhbrKvW04md3nRv6q8C4bogMVljtCaRMIo2NVNsE',
'Reward Panels':'122S-3pnDNoGHfTQgxl-tbB_7yhFhbnC7u1xbuiRpKt4',
'Forced Prompts':'1HBRwDeho6dcDIDpX85VNe4a8tGNkNFw6ctHy6z05hnI',
'Modals':'1hMA36tmuOxEu5uMhIREpvIFi7YTxkdlhFw5NydqjTDc',
'Congrats 1':'1__gLc9PW0tpqnecZcvbhntCCgmMYPSk7KR8PAwLgEpE',
'Popups':'13GzXbhAFwG4Kfz8sY4eo-uZZJl-9d_Wt-Rk0XrC3LWs',
'Congrats Events':'1MDgwZ1uolf27i1KHbV8P6-56MUyGYP8FxDox8Im39RY',
'Congrats 2':'1-FzgktsrnyeZwwBfNMnSVpyFpbS-p1IaqlDK78sjiHs',
'Congrats Purchases':'11QYi9qhOhajJR8W_DW8skkG-04Q34VL1HtjcIs8fa-o',
'Test2':'1SWiQm-O8MSJZJz7Sa1EsIOBj6Jl0clNNyTw-dawaEQs'}
def get_file_name(peth):
    current_path = ''
    for index, part in enumerate(peth.split('/')):
        if not index:
            current_path = os.path.join(current_path, part)
            continue
        if os.path.exists(os.path.join(current_path, part)) and '.docx' not in part:
            current_path = os.path.join(current_path, part)
            continue
        else:
            return peth.replace(current_path + '/', '').replace('.docx', '')


def get_page_links(docx_text, header_data):
    for url, data in header_data.items():
        clean_context = ''.join(e for e in data['context'].lower() if e.isalnum())
        clean_text = ''.join(e for e in docx_text.lower() if e.isalnum())
        if clean_context in clean_text:
            # print(docx_text)
            print(data['context'])
            print()
            print(clean_context)
            print()
            print(data['name'])
            print(url)
            return url, data['context'], data['name']
    return None, None, None


def read_headers(docx_file):
    document = Document(docx_file)
    headers_data = []

    for section in document.sections:
        # print(section.__dict__)
        # print(section.header.__dict__)
        # header = section.header
        for paragraph in section.paragraphs:
            print(paragraph.__dir__())
            headers_data.append(paragraph.text)

    return headers_data


# headers_data = read_headers(docx_file)
#
# for header, text in headers_data:
#     print(f"Header: {_}, Text: {text}")

# exit()
def main():
    print()
    print('Getting document datas')
    embeddings_data = []
    # convert docxs to plain text
    docx_files = []
    # convert docx to pdf
    for root, dirs, files in os.walk('./data'):
        for file in files:
            if file.endswith('.docx'):
                print()
                print(file)
                if os.path.isfile(os.path.join(root, file.replace(".docx", ".pdf"))):
                    print('exists')
                    continue

                doc = aw.Document(os.path.join(root, file))

                # Remove all comments
                comments = doc.get_child_nodes(NodeType.COMMENT, True)
                comments.clear()

                # Remove revision marks (edit suggestions)
                doc.accept_all_revisions()

                doc.save(os.path.join(root, file.replace('.docx', '.pdf')), SaveFormat.PDF)
                # docid = find_document_id(file.replace(".docx", "").replace(".pdf", ""))
                # docx_files.append((os.path.join(root, file.replace('.docx', '.pdf')), docid))

    pdf_files = []
    for root, dirs, files in os.walk('./data'):
        for file in files:
            if file.endswith('.pdf'):
                print(os.path.join(root, file))
                pdf_files.append(os.path.join(root, file))

    for file in pdf_files:
            try:
                name = file.split("/")[-1]
                doc_type = 'document'
                try:
                    doc_id = find_document_id(name.replace(".docx", "").replace(".pdf", ""), "1fFNdrhD5ZbkVTb1uX4-tWuDiU-T4odCS")
                except:
                    traceback.print_exc()
                    continue
                if not doc_id:
                    raise Exception("=======Couldn't find", file)
                print("full_name:", file)
                print("name:", name)
                print("doc_type:", doc_type)
                print("doc_id:", doc_id)

                header_data = None
                if doc_type == 'document':
                    header_data = get_header_data(doc_id)
                    context = ""
                    for url, dataz in header_data.items():
                        if 'linked topics' in dataz['name'].lower():
                            for line in dataz['context'].split("***")[-1].split("] "):
                                context += line[:-9] + ", "
                            break
                    if not context:
                        for url, dataz in header_data.items():
                            if 'transcript' in dataz['name'].lower():
                                for line in dataz['context'].split("***")[-1].split("] "):
                                    context += line[:-9] + ", "
                                    print(line[:-9])
                        context = context[250:]
                    print(context)
                else:
                    continue

                meta = {'doc_name': name, 'doc_type': doc_type, 'doc_id': doc_id, 'doc_path': file}
                with pdfplumber.open(file) as docx:
                    for page_num in range(len(docx.pages)):
                        # do all this effort to get the most relevant link
                        link = f'https://docs.google.com/{doc_type}/d/' + doc_id
                        if doc_type == 'document':
                            print("num:", page_num + 1)
                            docx_text = docx.pages[page_num].extract_text()
                        # Generate embedding
                        # embedding = model.encode(docx_text)
                        embedding = []
                        # set metadata
                        metas = {}
                        metas.update(meta)
                        metas.update({'page_num': page_num + 1, 'header': 'Page ' + str(page_num + 1), 'link': link, 'context': context})
                        # pack chromadb tuple
                        embeddings_data.append((embedding, docx_text, metas, doc_id + '-' + str(page_num + 1)))
                        # print(metas)
            except:
                traceback.print_exc()
                continue

    # recreate collection with new data
    print("Creating database")
    os.makedirs(constants.CHROMA_PERSIST_DIR, exist_ok=True)
    client = chromadb.Client(
        Settings(
            chroma_db_impl=constants.CHROMA_DB_IMPL,
            persist_directory=constants.CHROMA_PERSIST_DIR
        )
    )
    # client.reset()
    model = SentenceTransformer(constants.EMBEDDING_MODEL)
    client.delete_collection('realtalks')
    collection = client.create_collection(name='realtalks', embedding_function=lambda text: model.encode(text))
    print([elem[1] for elem in embeddings_data])
    print()
    print([elem[2] for elem in embeddings_data])
    print()
    print([elem[3] for elem in embeddings_data])
    collection.add(
        # embeddings=[elem[0] for elem in embeddings_data],
        documents=[elem[1] for elem in embeddings_data],
        metadatas=[elem[2] for elem in embeddings_data],
        ids=[elem[3] for elem in embeddings_data]
    )


if __name__ == "__main__":
    main()
