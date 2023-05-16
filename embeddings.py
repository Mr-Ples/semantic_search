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
import re
all = [('Logic Is Not A Lie (Podcast #64)', '1zjZ9OZCSElAIQSLKfPgxN8AkrbxSd0qBKLa7DcjWhqs'), ('People act based on their wiring, its just that simple', '1hRMi2tU2XPV9tUVb4UOsmHnuUB9vas7QtVXp3VRcC7Q'), ('People act based on their wiring, its just that simple', '1HrydCxKFvZMlGfdq7EOXK9Awwh9VC1jHs6_T73LjQ-Y'), ('Athene Real Talk Archive #2', '15L-Uvqmr5HBc3A8tndRo4i4ayl6j5cPX7oEzkXNvWgE'), ("'Choose to not amplify the thoughts & emotions that involve you.' (Podcast #113)", '1yIKJbUAzVFJGeOYbm6q7Q7eZrAaVxcpztmqB1hN-gH4'), ('Being Selfish (Podcast #59)', '15hRGTGtCREDEoAgDGS6XkjDSPvVrXeEpDmOMOfU9UTU'), ('Life Story & Low Self Worth (Podcast #58)', '1JOKfFlLfdp49xxTE0qtzOq8CizAnjgoAk0KYjzgi53A'), ('Guided Meditation Step 3', '1vlu6Jt8nqu2oZUYesprcz3GYDC8ca6PiOhNTb5NPpnE'), ('Guided Meditation Step 2', '1iYLqp-4ck0RxUrPT5LVQS7EDUcjCr1TnI3tmDGdkjW8'), ('Guided Meditation Step 1', '1UScixys2qZ6RraqLzTk37JESqSFxLZ6q2uq04xC0wao'), ('Emotional Intelligence, Religion & Accepting Reality (Podcast #57)', '1LA0rZAWPi77qzKaN2_2yOLW-hnk3KXdLpzKxOor0spU'), ('Living for Your Parents Approval (Podcast #56)', '1bSEOAVmB8kuwfQgbjke4ea-eWCspcw28wlMTtHSwE08'), ('Identity & Changing Habits (Podcast #55)', '1R7SyoKz0Cfc77Dy5niO3MNEr0lqGQNBgCSLeXJR9h6E'), ('Skype Calls with Clickers #1', '1goqw35u2NLnW7XZkc-mvdmSNvGYcQU5cr4mn0U2YsoM'), ('Low Self Esteem (Podcast #54)', '1kN7JpDF5QzhcDOW1imsKmneltARrdPslO01dYf8CGrE'), ('Believe in Logic! (Podcast #53)', '15DnpuuTQ45v2gQSvDRRK2rmhZjiaSZQXie6qsLcDtNA'), ('Athene Real talk Podcast #8', '1hHtuK8Fwc5hiVSO1sd5qEKAiwZO-p--GI5bHybVcQt4'), ('Athene Real Talk Podcast #6', '1SPNyFtaNM5IW6Ty1sl7IKWf095LgO0fJId2I_eLftmk'), ('Aproval Seeking vs. Validation Seeking (Podcast 61)', '1P9nJRUEYyqHvaPqacYVueoEBEIPSdrvYMdmhMkzBvoU'), ('Athene Real Talk Archive #5', '1urhWzPxVa6XlCj87nJVzPhB2AbuWMprq4NR95qWh-cY'), ('Athene Real Talk Podcast #11', '1Z7Fpney0x9SbXSmC2KTO5gwOU5i2ccevYLVzoRBQpnE'), ('A Theory Of Everything Or A Psychological Revolution (Podcast 62)', '1SQ3Vgcfb1_go_Qs2ih0oHfFuz0WdDrogWtlyHJ6r8Z4'), ('Aligning Your Self Image With What You Truly Are (Podcast #63)', '1VLeO6MRlw3fHiByx3ZICz3bINnFaJuSPv1wNZ4FO0BM'), ('Athene Real Talk Podcast #1', '1_Gx2pa2BLYWm4IqA5jQOaMG55l-gLW7vxJEIZy_CMSY'), ('Athene Real Talk Archive #1', '1VnJOlhBn6ib_PWBR7yEKUAE_bH3pDpJYQqVGggp3zH4'), ('Athene Real Talk Archive #3', '1LmIdR-4dx_YrQv1gDAOkCxsMeKJNNJXJYoeh8gscmUo'), ('Athene Real Talk Archive #4', '1xdYEaJLayQfXCQPizZwl463E3LHewUPu4BpdlOv2y-Q'), ('Athene Real Talk Podcast#16', '1icK0nITxdVhLOEiRyQSRheiqm8vDt_c3W4anBxWNckY'), ('Motives Part 1 (Podcast #120)', '1f8lN2IDI95IyCWnSzO9PlHv9eyWQtST0_Y4V4S3OQyo'), ('Athene Real Talk Podcast #4', '1kWjRV8Gj48yXoZsJwvPcunLCr38YDY5XIyL-zKnuCI4'), ('Motives Part 2 (Podcast #121)', '1w28RQOnaJYhh0ZoPCqDYes9m4vPXafB-pRmxjhORWKU'), ('Athene Real Talk Podcast#21', '16JqFTpVvPJbbFUpGnCEw6AoDUNfKkiAxDOWbrkIcNaE'), ('Stas Talks About His Click (Podcast #65)', '1Gb8fnoFoRMpROHT_K5_KXTpWL6cMXHEJmbo9EleQbgM'), ('Athene Real Talk Podcast #5', '1F6hU8EGYM5aCRkMpkqBHkDPHCviWiq2Aqw_jZJVASs0'), ('CogniProjection Part 1 (Podcast #124)', '1Vc7__04mFAH8vUaAuq7nS15Y0h9YjghOuCw6NfDWby4'), ('Athene Real Talk Podcast#22', '1ECdnbdTwml0jNXqujzniYAGdNPmsFyZ0xk3aW_hhLRg'), ('Athene Real Talk Podcast #26', '1Wk0yBJUaX4GGT9wACokuscnTfS0hONvsdIqbHpvu-Zc'), ('You Are a Slave to Your Emotional Core (Podcast #66) (CONFRONTATIONAL)', '1ZbY6Rbgj7jMMn8oQ3gX1CryQDfFZY4Z64wm6mvD-QmY'), ('Cogni  Projection Pt 2 (Podcast #125)', '1u-TJvsN-OReQAYur1qyoWbln4TDPrd4Em-QOt_I81lg'), ('Athene Real Talk Podcast#24', '1cjto-Y_5o6c53lRsxaJwFEciQtQzVBq5PrQ-NRmf4tY'), ('Athene Real Talk Podcast #27', '1-O92HWMo5m63awq44Qf7Dwedu6d0MTiA-B1w4hjm5l8'), ('When I Walk, I Walk With Logic (Podcast #67)', '1ldEJ5t7RMJhMGF8A_vGldCPGf-1bRuspdD1tYm2iknc'), ('Athene Real Talk Podcast#19', '1M-Y8UQTkxrpWQzFvIjkI7MA65sZOlGHzIi1VXZM5cpg'), ('Athene Real talk podcast #9', '1cajI7roBQ0m4WBCCDGtVEQ29bXgksqF2yTmvj7ZiQfo'), ('Athene Real Talk Podcast #28', '1Fc0heUOqVIcjpt76R1tVD2OpLZf2QpWTHP9aQPDFgEI'), ('Riccardo & His Click + A Reddit Testimony (Podcast #68)', '15Wua9dSEdW_lnoFzjcWYgok-0vUA3Fa_R1WHFmAi6kY'), ('A New Way Of Clicking & Patterns and Consciousness (Podcast #69)', '1ib9bvmftSKLliqukyI9HyD3CxWU_Fzi-aREyXjdpLHU'), ('Athene Real talk Podcast #7', '10t2a4Q-cS0mCf6h8e3aUCbUsKMwg4qtv4-tM_kFkON8'), ('Athene Real Talk Podcast#20', '1iKXFcjOmNCTyMXnm3pdpxNjFo21PHPTXkkeMd5T_eD4'), ('The Intersubjective Reality Defines The Comfort You Feel (Podcast #70)', '1XE2LzR2s1eY0j_Aa1sc-N17st8PBrDMGdqKILUO5Ioo'), ('Athene Real Talk Podcast#17', '1iIauYx56YtdjvXPvH1ua-DrVNhkLSndYQoa_pZyjsEI'), ('Athene Real Talk Podcast #13', '13HJPxwONfyQ_Kv6ZmRydHL3dY4u9FvqaPF7OgkFJtAU'), ('Why I Act Like I Act On Stream (Podcast #71)', '17k_uYhcF87OyosawcUwwbknhcMdJGgYi7ajmwuUXUy0'), ('Athene Real Talk Podcast #3', '1B-gSAlOnOE47WJZkq8o0lP2hW9jz1Nmt0tmqsFhnAeM'), ('Athene Real Talk Podcast#23', '1OczUGIXbbvLCKy7gywjD0Uc2O1f2chPLnuma0Eu6RBM'), ('Experience Is Just A Tool, Not The Goal (Podcast #72)', '10s2p87mSZlAN7AU2AEEWYR7oqvvAGR0yJxr1d5fg6Fs'), ('Athene Real Talk Podcast #12', '1_-qKf88BTka04_9r8GnEvTIFhdcXjBbTsqiRk55B7LY'), ('Athene Real Talk Podcast#18', '1Wc8hkmlpEUVJakw6Kr0A_cWRFa5f2PHoaSRflJ8r6po'), ("Don't Have Other People Tell You What To Believe (Podcast #73)", '1NAvszlP9k36lx6cH9cGeaspVir4zDTR4mMvUDaeI4lo'), ('Athene Real talk podcast #10', '1_zgqh2XXSyMKcR92ZeO0IO1Sy63OFQ-LSCjj5EmofQg'), ('Testimony Real Talk Podcast #1', '1i8urZvW3-SvpQ-qyT35VnIcOeuQzXa8gqK4O0By-QSM'), ('Athene Real Talk Podcast#15', '1cXzMLQ7B46aXXctiBCSpH0gCJFbQyyKXho2HORt5N5g'), ('Athene Real Talk Podcast #25', '1lBNd6GNTYnFZg3q_bzM5T_v9XesIBnsGiSjhF4fBFLk'), ('Athene Real Talk Podcast#14', '1OWOlnoCd6s5iI2fRUIfy_OSnGFa0r6HqnzPMN3nCt6s'), ('Stop Lying To Yourself! Podcast #74', '1uBowKwCcZy8CkpCU_vwVD0kv3G7X02UH60Jq-vm9Xfs'), ('Athene Real Talk Podcast #2', '1CrbzbuERETEhf4lCEq6W-vpihGuTC-E3Wwvm9VhFJHM'), ('The Click 2.0 (Podcast #132)', '1OLdHMOqQT77vvHYfiYuLFK5oHnJR-6aw9g9CkQ0VGyM'), ('Athene Real Talk Podcast #44', '1K2fzVACcPjF__h0ufESHHT6Bl4EAv1BNgTUH3ZjKN9A'), ('Most Confrontational Real Talk Ever (Podcast #75)', '13r1DAmrpC6VOMEVYcze69cnn-KIOgzYj1fEp80XBgeE'), ('What Is Consciousness (Podcast #76)', '1FNgF0QXLgMFP0WoNbw0eCANO6i7Svzi73P2VQT-ISNg'), ('Athene Real Talk Archive #6', '1fShFK_EIzF1BSighsGod-RdY_I1yftRtAcQpRsWGH2Y'), ('Logic Is Inductive & Growing Up With Fake Rewards (Podcast #78)', '1lSC3goxCSWdrLq8x-Yo0h1-XvWeYqmqLcewYsv9OPFM'), ('Athene Real Talk Podcast #30', '1ySfbHmQ8xmyE9uT-0qQzaYrJZ_C3bBHaPP-OYgdnQqE'), ('Athene Real Talk Podcast #45', '18Z3bpd6nsrokPKbGrbPDnvBK0ez6n8S_S49Jj5S-xrc'), ("'Your drive for comfort was your drive for logic all along.' (Podcast #79)", '1eozZMe-gh5Xo0ShUssfRBQSn_x95abokYOtYEyUReUg'), ('Think for Yourself (Podcast #46)', '1gDXHHU7GVgjoMctHBCBIpyhkLAeQNqXh5j4c-9TtNKY'), ('The Click, Start To Finish (Podcast #80)', '14YGad4J6dDRjBnmAiIHKUf3cIMkLRpff1lpOmkcAIJc'), ('Performative Contradiction (Podcast #81)', '1jKtSIAkRiahZC1-0UArwRupDso8iAWgT7hjZq_FZcy8'), ('Self Image VS True Self (Podcast #47)', '1h8kejuNLSV30o4QyR0NEhVRxeHp8WHpJ1tKvL9wQ_lA'), ('You Have Never Been Taught To Live For Something (Podcast #83)', '12u4Dcdoxnn8WOcQ963jIVMU1gSGm-Znm6UoDfHG8pMw'), ('Reality Check (Podcast #49)', '1oC6Pm-_t2rLbt_ZtP8VDNwnxRbqEjR8DQ1KoFb51Ifs'), ('Reese Talks About Probabilities (Podcast #84)', '14dUHhZcdHpwPxkqnCvfn4GY_aLq0-yK6ENitTl0ALKY'), ("Critical thinking and question 'Comfort' as a core value (Podcast #50)", '1i_ecffhLg3ERS_NWo2n2ZKNEEK-uAmb-YU_xRLut9yI'), ("'With thinking in probabilities, you don't care anymore about being right or wrong.' (Podcast #86)", '1lKvSfcROkrq86Xj2-5CiTreNIl8o3WGkhoeqheQb4F4'), ('Athene Real Talk Podcast #38', '1WVT2Yxo7lvb6AcBAujUxSqP-FFIpFppgIv3YFYzaN8E'), ('You are all idiots (Podcast #51)', '1wpLtxU5aC5_yzwjgOT8Nx5JN5vkk9WEq2X0UbQ666lw'), ('Athene Real Talk Podcast #39', '1o-MW1Wtm0pTfkVLE8ypZRL8T0AKlBOfUlZ3tyhhvIOQ'), ('Athene Talks About His Ideas And Way Of Thinking (Podcast #87)', '1DXJITVfKLPVOpp54oK_AKHBedharutKZun7fLhHq0LI'), ("'People just don't want to change.' (Podcast #89)", '16ajzIqvtbF73U9xNsHnE5mnUJjmfYGMCWxY0Fhffv28'), ('Athene Real Talk Podcast #40', '1jzWA7P6-Esxu2sf_jSzHMW3jYQeIT_Hj4C2Cdc8Y_ig'), ('What Drives You (Podcast #52)', '10T_9SqNpBynam9dV2_0vaHEL-uIWARlLHj2PKUReqQ8'), ('Athene Real Talk Podcast #41', '1Ee1046VEh0WjjK-fdtfq2WSWJj3GCa2u7EMB99gmLD8'), ('Athene Real Talk Podcast #42', '11TccGlds4uV2tMzu9aBMJpHR5o6Qd895vI6q6HnGUUI'), ('Athene Real Talk Podcast #43', '11WWSXLWcwNmAJtX1HPcl9zcex5EQHkISV3TCl1SBc2w'), ("'ActionReaction is omnipresent.' (Podcast #101)", '1ItfwhZvIg3uiw6fCLjEcDf1Kd1cqyXFjZH4_YOeRF84'), ("'You are so conditioned to just trust your environment.' (Podcast #99)", '1kdjurLlkT3JYcW_4QHwiZaiKJvPA0vXE4oKX2Q_O-4Q'), ("'The Experience Of Choice Is Screwing You Over' (Real Talk Podcast #95)", '1Vs-WggNybdZPrk4V_TdwmDoGcoidxlKbCFTdOFm6PSE'), ("'People always give away their authority.' (Podcast #176)", '1R_mccdadD9HU8gP-5Al2_s840zbsXEIjHp-CVX1W-Js'), ("'You Do Not Get To Choose What Your Goal Is' (Real Talk Podcast #95)", '1DaqW49Q3oJYe-myOYWifpk07818elTWqEoNJbcJn9K4'), ("'Valuing change is important.' (Podcast #93)", '1AjE9thUzUbbJZKfnWLSBh92e4BKv79GBE-43oqMQ-Kg'), ("'Learning is merely a tool to help you take action.' (Podcast #174)", '1eyjhlegtoRuQhB10Iiwr4z0IX1zQX2ddjWY-KE3sT5M'), ("'I don't allow myself to make it about myself).' (Podcast #175)", '1PkyZfQDYg47SIMLgKxwpX_nUc2yHX6r7sO1BjMplvGM'), ('Afterlife, Quantum Immortality And Cognitive Dissonance (Podcast #172)', '1CRXhKJj7XSl92gUAkciiLiF_67hgOomA433Wp5QzQuc'), ("'You'd rather hate your life than change it.' (Podcast #91)", '1sc1M4zFLI_mKMdxSsq8D4yzHhVXDhWGN7iiO89wcCX4'), ("'At the end of the day, I just wanna do as much good as I can.'(Podcast #173)", '1bx8CIwsRQTQy1C8zdXpfmdrV8UTV7M_Dh-D1iJO3JV8'), ("'Your value isn't defined by how hard you work, but how hard it is to replace you.' (Podcast #170)", '13pjLtHmlHaCsBhmhNuTe9gB7a-8JAmXvjqugtIsKcKE'), ("'Information Theory' (Podcast #171)", '1_ZaII4Hi1-4y5HrpssMkfxbalviuv9xc3oVmWrtuL3s'), ("'Embrace failure, but don't try to chase it.' (Podcast #169)", '1olXXGW72qqpGkW9LNdzXBoYSbIiQ6FmE2GJ6RGctVYk'), ("'If you don't want to work, be smart about it.' (Podcast #168)", '1RkzmTtb9wn_5c_DC9CZwb0i7yau1gIXgx2P7IfuRU7A'), ('Guilt Tripping, Default Mode Network & Fitting In(Podcast #167)', '1sQsmNo1c3zS1eyL6wN3LZ71F9QlAbqT6IUhaejwDvCI'), ('Athene Real Talk Podcast #37', '15yaoKfscFs23-9UsizlGsrYU0Xmy5h4vhnNGnQlOhuw'), ('Athene Real Talk Podcast #36', '1M3cryI7VXA-n2ofDOmd9p6MoNO68xiOeeuOkk__CZ-M'), ("'People want to be right because it gives them safety.' (Podcast #141)", '1LxY9Q08N29d2_0RYIJgGIafVlvY6oOs0ImuIshVOVlg'), ("'Your Emotional Needs Are In Control Because You Don't Understand Them_'(Podcast #140)", '1CFJI5JnG18YE1Bp-ZyjYfRxELhqgyHiYncL3mGu5rSk'), ('Athene Real Talk Podcast #35', '11Im3pQG3LKj0jPhthwBB_GFuXR5sBJ9l2_ryiG5oiE8'), ('Self Image, Logic and Confrontation (Podcast #48)', '1l_ULHh7ucNKt7YSE1W-e8-Kp9LH5_NvsCNHhx9Rgsgc'), ('Responsibility And Awareness(Podcast #139)', '11k0uBP5A0YGFHSvYDTyaGDRLr8xEzbBoneQat7v0CVg'), ('Athene Real Talk Podcast #34', '1XckrgVs9OhKa4ZMxdHkDalkYFl3Qt6KFD8foGBSFr0o'), ('Probabilities & How The World Is Probabilistic (Podcast #82)', '16M3UZQcfqcjsvBZ1ve3CfDzhMjnGQwiMJa9eaDkrIDs'), ('Identity, Needs And Beliefs (Podcast #138)', '1UiGTbZJAGxAiRq8CnJbtywRwXnWRfD0kFsbZQDFIoE8'), ('Athene Real Talk Podcast #33', '1yfPcbviOf6eLK66hhFO7HnwHuJcE3cdCnnXXQpYSWa0'), ("'Understanding can make you really overcome anything.' (Podcast #137)", '192kAMzThDQvUbLO0tiBj8GRu_9_MeMGHYkmXUgjd94E'), ('Athene Real Talk Podcast #32', '1xOhzO7-Crd-qj0wRxGI9mCXugqWgpXDbofR7UE0qrsE'), ('Debate Between Cocky & Philosophical Athene (Podcast #136)', '1cRznfR3w_NgWbf8cPGjKwpWWLqDQ6fw2LumS0ZKgH-w'), ('Athene Real Talk Podcast #31', '16PImipoeDinargVrmX7D4PcvKBbJAiSU45XxVkQIziQ'), ("'Why I became so robotic.' (Podcast #135)", '1ogYnr8xZKsq2H4d3kwhpAJj6LiSIMGy4tm95lidTc98'), ('Integrity & Relationships (Podcast #134)', '1zh0EKDFZCBRwIX1mwZHWL5m2Kg9vLd3gy-B2pLMuBcI'), ("'Talking About My New Approach On Stream.' (Podcast #133)", '1XPGQrcszItItRHfmNT2-KlF1pwVse9NUaIm7HH-P9C4'), ('Athene Real Talk Podcast #29', '19t2HWS7OfhenAKJusH_fKylI0zVeEp2ZETIvjMvYzdM'), ("'We live in a world where everybody is actually enhancing each other's anger.' (Podcast #131)", '1UABtMf5sXKgfGIkpGnHj-958m1atUvEiG0M30BAIivY'), ("'For being understood you also need to feel understood.' (Podcast #130)", '1x4KQtw-OfnJ-p3oVNzSVsTYE8ZLpKt9WMcgO0zvPmgA'), ("'Find the abundance in what gives you confidence.' (Podcast #129)", '1J7cpXxbHn98vVc2kL7Bv7mXdLnxyxVr6uTP36Dh8UQA'), ('Finding What Gives You Confidence (Podcast #128)', '1qkzeTshJ8QM9g9E2Nl6R9BhvyUngvR6JmLvq9HF2iPU'), ('Being Outside Your Head (Podcast #127)', '1SOc7NbcmQrViw5dfAOgFz7Zeh63id_3yzozNEn05HoQ'), ('Talk About Morals (Post VeganGains Debate) (Podcast #126)', '1DaAk-J9lub2Y2_pRwP619GgGkola4kwyHvv5KznLH5E'), ('This Will Change Your Life', '1gIbNRDx2Kj8ESDykbA6D44ApfDT62TqmV-DUjUYgn9A'), ("'Consistency is within a framework of what you are.' (Podcast #123)", '1A0GCm69PsUeO1diCf9vXlfCLYz14SnCrBKQiE2GeaTo'), ("'It all starts with a choice.' (Podcast #122)", '1WnkbJi9NURLgkgYrS0TjbAYCEZe8jpl1uKDf0j6Z5IA'), ("'People have the idea that they get to decide what to do with their lives.' (Podcast #119)", '115gfFij06yVH76ekNef-mPIyrFd3QbEyqHvxzmT_K84'), ("'The reason I achieve so much is because I never settle.' (Podcast #118)", '1as1kdHGvPV0iYv3P99WE9OTHz8shMayHKgeSFWwHIgU'), ('Brian & Riccardo Talk About Logic (short) (Podcast #60)', '1vT8Mvbj2GJlBQUVYvTXe8ocAfvslDBoyDC2fMxqSQvE'), ("'Understanding doesn't mean being a logic robot, it means understanding yourself.' (Podcast #142)", '1MOiZmeyQQtjab3wVA7VYqxBU-qPae4sob1WXpw-LOx0'), ('The Hemispheres Of The Brain (Podcast #143)', '1BUX-muIN9zIyPJhENC04SBAjW5UGPuDBivoU2TBcUtA'), ("'You can change right now.' (Podcast #144)", '1VaCwm6ox2Ok7VMXo_mGUMne5YUASNwfVRQVw0xNEUBM'), ("'Actions and reality speak louder than anything.' (Podcast #145)", '11nm3l5b__brEqcJwuoyNA0vDvAzuMH-2UKrGddN15F4'), ("'What is information What is our essence' (Podcast #146)", '18HwAzoV8Gm7l1-GBnS3-8ClEasRcWw5S4ORICQezDi8'), ("'Settling is a bigger threat to your safety than pushing yourself.'(Podcast #147)", '1aDNaDEwKcqPVRDvfhaW12p5jQ7JNc-Y8kTINMQX4hwk'), ("'I believe everything has a logical answer.' (Podcast #148)", '1AbXzQ0gMxR9kg-9gKU3xHxsuTtUxmIdkA2P8xXdUY6E'), ("'Why do you guys settle' (Podcast #149)", '1hM9sdMMbFXKpO6bJYiFn5kKkby0h_v9LkKJdUS31LjM'), ("'Life is not about what you want bro, life is about what is.' (Podcast #150)", '1P5SWVumzmOjq0K5xUwzcotEhRNncViAGh8cf0nIr-iU'), ("'We all have a sense of entitlement.' (Podcast #151)", '1u2LZF1Fcnp8U8WawmtKADA3xCQWWw2dIXfsi-fiXSuY'), ("'I know I am merely the result of my environment.' (Podcast #152)", '19O6KoUl0spFm4kaCtkxnmvKIO4w_dsSxDAtQzIhZBE4'), ("'You come here to grow up.' (Podcast #102)", '1JSrcEofiAFJ70ezChB8S_4rVsJdxWKR_JecgU1-4elI'), ("'Every person watching is more intelligent than the average guy 4000 years ago.' (Podcast #153)", '1zLdWo0M3x0GzhDZZCD25CBUKlM2cJjRglhZ-N4-LQYw'), ("'Relative to the universe, there's no purpose.'(Podcast #103)", '1EjoIU4DbOLmqvgdqsuPF1AZ4jA4V9S2lL6GABpftaNk'), ("'I am the most intelligent person in the world.' (Podcast #154)", '1-flmFy1E3QLEArPUETSiHeZCiClRqNpBRXJBpNa53Z0'), ("'Saying life is about happiness is an insult.'(Podcast #104)", '1sMr74yB092GWdC77tN9zExWPljjNxz70uz9VwHQuG4c'), ('Veganism and Vegetarianism (Podcast #155)', '1iwu_O4bLyk-QHuTj1uoVYly2l64zaOWqeipCBi2SGrY'), ('I Wish Athene Dies (Podcast #156)', '1LLQzz-G_f_WAS6SJxa41LNbLtxGv1JigNXw9Okd8ew0'), ("'Don't be attached to all these concepts.'(Podcast #105)", '1Kgz5XOKXUFQoUYwQe4MRXH0vJ_EybumqR0eYZaQ8hWs'), ('Intuition, Trusting & Loving yourself. (Podcast #106)', '160AisEfIZcB0ghOcFFLSj1RqFi_FMr23wrVQLN1wklk'), ("'Things are just the way they are, you know' (Podcast #157)", '1nf9vrpnbCwSFlNIe1PzCd8X2QZJeefuAKiJnGjGBWRc'), ("'You can already process what you're afraid of before it happens.' (Podcast #159)", '1qMRDLgBQhUkBcAAd6spZrTQtKURUN2iHAd9nLdxb_Ks'), ("'It is not your fault!' (Podcast #107)", '14elFpGJiH8BHHyZgZ88WZ1oUN_YpcosSFUQj1LtHz9E'), ('Dopamine And Serotonin (Podcast #158)', '1Jwl_gduc647hWriPRjhDTDSZfLUbdinl7QXOFBEd-3M'), ("'You don't need to live this fake life!' (Podcast #108)", '13lA2Gex93kLqkrbPtxIu7Jm07234Rqn2nYPSqFicThU'), ("'You can run away from your problems, but you can't run away from yourself.' (Podcast #160)", '1U35Kx-XOmW4Va3pRw8fb0dDFUd7KGnpX2py-2t8znbk'), ("'Trust your reason, it has answers to everything.'(Podcast #109)", '1EP7eEWmGxOFBJgIDjJhnQ54_97vwhDSreL2H6VcOkP8'), ("'Athene, how do I join your cult'(Podcast #161)", '174uUBfwO-y5BGUpNDKdH5-UlKjGy14P9-vgEr-AhhxY'), ("'You actively make the choice not to care.' (Podcast #110)", '1HJDV54gKmeTDjkm8xIkXNB-uK3uduWjVMWYIZCN-dnY'), ("'Are you right now the best version of yourself' (Podcast #162)", '1BOn0enD8e9q-c24Jh9YIaWRDOQlY4SbR2JXTU-zFBIw'), ("'Reality is that you have a better life than most people on the planet.' (Podcast #111)", '1Rp_Rd3zZFU3SxzFiiQtQIi3zAMyxkr9ViQXPbpTtTsg'), ("'The Singularity Group.' (Podcast #163)", '1bMt0eoqC1Y_UaThe08KVouJJpCrj3b0lcaLC4ItFerU'), ("'Heaven & hell ain't after you die, it's what you breath every single moment' (Podcast #112)", '11RDk2afKu5FKfEa8cjtCT5LeZHnwHseIct_L914kqRE'), ("'I don't let haters define what I can and can't do.' (Podcast #164)", '1DmZc8gmXgOt9ghEfXducoUKoTUPZJ_9HxdRQNACMtMc'), ("'The Red Pill.' (Podcast #165)", '1anegDXgf4nQwL6ha2nftJyalRzfBwMtu9BmvKD7uGpo'), ("'Everybody, whenever they do anything, they always have a motive.' (Podcast #114)", '14kdQIwLVrTLD6vz1zAAghzuozSpBy2p2mRl0vl0q2x0'), ("'I will always push myself.' (Podcast #166)", '17M1gESRdb0_6G_uGM7SIGFAExI-7WSBJf6uQ-ya_1EA'), ("'You close your eyes for the good.' (Podcast #115)", '1YJTCrk3frKR02_Osp1p7OV-P1N3Ai7aE7x2zIBUVq1o'), ("'I'm not here to fulfill my own pleasure, I'm here for a bigger picture.' (Podcast #116)", '1DEugdbZHXM9e4QeGMkpqB3G3L4Il-7t9EZnxGlBiLqU'), ("'People always give away their authority.' (Podcast #176)", '15dMCvhUCtyf-2AZU9h7OEykWVz9hg2-CB_QGL-SpwHY'), ("'People care more about themselves than about honesty.' (Podcast #117)", '10XzTRmjJ6IBRirKZdlA_ekbKTt72wQ7LRkumF-IUlCY'), ('Guilt Tripping, Default Mode Network & Fitting In(Podcast #167)', '1ycyyMJI5aBeiCv6f6gsk38FFpF5mkeKXAswC8UnHg_A'), ("'If you don't want to work, be smart about it.' (Podcast #168)", '1fx1jewAN0b7fAQLWYUimf-1orB_EhprIy9F6hpNhdXQ'), ("'Embrace failure, but don't try to chase it.' (Podcast #169)", '1whCgNJCQqcLvC76nZ4T0rbMJDmpbO0JH5_s46njxHp8'), ("'Your value isn't defined by how hard you work, but how hard it is to replace you.' (Podcast #170)", '1FURVT8yBUC1VQQFgABgUAFu4pJdqJkRjrzWK5M69adM'), ("'Information Theory' (Podcast #171)", '1QGwwT8hFhumyogM3YxkAW1Ou23a_CV6c_HcAo7qJwHU'), ('Afterlife, Quantum Immortality And Cognitive Dissonance (Podcast #172)', '1oZMWjZvvycll2Ucq47gt-foMytV_RXYTqGnJyUcTfVo'), ("'At the end of the day, I just wanna do as much good as I can.'(Podcast #173)", '1qoz2QGNucDD1hRLn87Uz-1KoSPvNvIe2LiNvJrrCWP8'), ("'Learning is merely a tool to help you take action.' (Podcast #174)", '1Mebwa7NW6DYfOeUnVcUDKWcDXR7VWCAes4siGYVGIII'), ("'I don't allow myself to make it about myself).' (Podcast #175)", '1tUrZ3b4Gt-jD5tTx0F5hWZHwPy4zwCaF6UCVGzeB56g')]
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

    for indexx, file in enumerate(pdf_files):
        print()
        doc_id = None
        try:
            name = file.split("/")[-1]
            if name.endswith('(1).pdf'):
                continue
            doc_type = 'document'

            # print(''.join(e for e in name if e.isalnum()))
            for nameall, idall in all:
                # print(''.join(e for e in nameall if e.isalnum()))
                if ''.join(e for e in nameall if e.isalnum()).lower() == ''.join(e for e in name if e.isalnum()).replace("pdf", '').lower():
                    doc_id = idall
                    name = nameall

            if not doc_id:
                doc_id = find_document_id(name.replace(".docx", "").replace(".pdf", ""), constants.REALTALKS_DRIVE_FOLDER_ID)
                print('https://docs.google.com/document/d/' + doc_id)
                if not doc_id:
                    raise SystemExit("=======Couldn't find", indexx, "", file)

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
                        fulltext = ""
                        for elem in docx_text.split('] '):
                            fulltext  += elem[:-9]
                        fulltext = fulltext.replace("\n", " ").replace('Evaluation Only.', '').replace('Created with Aspose.Words', '').replace('Copyright 2003-2023 Aspose Pty Ltd.', '').replace("Evaluation Mode.", "").replace('Created with an evaluation copy of Aspose.Words.', '').replace('To discover the full versions of our APIs please visit: https://products.aspose.c', '').replace('To discover the full versions of our APIs please visit: https://products.aspose.com/words/', "").strip()
                        # print(fulltext)
                        docx_text = fulltext
                        temp_contest = ""
                        for elem in docx_text.split('] '):
                            # print(elem[:-9])
                            temp_contest += elem[:-9]
                        if temp_contest:
                            context = temp_contest.replace("\n", " ")[:1000]
                        # print(docx_text)
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
        except Exception as err:
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
    # # client.reset()
    model = SentenceTransformer(constants.EMBEDDING_MODEL)
    # client.delete_collection('realtalks')
    collection = client.get_or_create_collection(name='realtalks', embedding_function=lambda text: model.encode(text))
    print("BEFORE: ", collection.count())
    collection.add(
        # embeddings=[elem[0] for elem in embeddings_data],
        documents=[elem[1] for elem in embeddings_data],
        metadatas=[elem[2] for elem in embeddings_data],
        ids=[elem[3] for elem in embeddings_data]
    )
    print("AFTER: ", collection.count())



def clean_everything():
    client = chromadb.Client(
        Settings(
            chroma_db_impl=constants.CHROMA_DB_IMPL,
            persist_directory=constants.CHROMA_PERSIST_DIR
        )
    )
    model = SentenceTransformer(constants.EMBEDDING_MODEL)
    done_docs = []
    for collectio in [
        # 'docs',
        'realtalks'
    ]:
        collection = client.get_collection(name=collectio, embedding_function=lambda text: model.encode(text))
        ids = collection.get()['ids']
        documents = collection.get()['documents']
        metass = collection.get()['metadatas']
        metas_new = []
        for idss, meta, docus in zip(ids, metass, documents):
            # meta.update({'context': ''})

            # if meta['page_num'] > 1 and not meta['context']:
            #     print(meta['link'])

            print(meta['context'])
            if meta['context'].startswith(". "):
                print('removing something')
                meta['context'] = meta['context'][3:]
                print(meta['context'])

            doc_name = meta['doc_name']

            removes = ['Evaluation Only. Created with Aspose.Words. Copyright 2003-2023 Aspose Pty',
                       'Created with an evaluation copy of Aspose.Words. To discover the full versions',
                       'of our APIs please visit: https://products.aspose.com/words/',
                       'our APIs please visit: https://products.aspose.com/words/',
                       'Created with an evaluation copy of Aspose.Words. To discover the full',
                       'This document was truncated here because it was created in the Evaluation Mode.',
                       'This document was truncated here because it was created in the Evaluation']
            if any([elem in docus for elem in removes]):
                print("remove aspose")
                for remove in removes:
                    docus = docus.replace(remove, '')

            if docus.startswith('.  '):
                print('remove garbase')
                docus = docus[3:]

            if meta['page_num'] == 1 and ''.join(e for e in doc_name if e.isalnum()).lower() not in ''.join(e for e in docus if e.isalnum()).lower():
                print("add doc name")
                docus = doc_name + ' ' + docus

            if '.pdf' in doc_name:
                print("Remove pdf")
                meta['doc_name'] = meta['doc_name'].replace('.pdf', '')

            print('https://docs.google.com/document/d/' + idss)
            # print(meta['doc_name'])
            # print(docus)
            # print(collection.get(ids=[idss]))
            collection.update(ids=[idss], documents=[docus], metadatas=[meta])
            # print(docus)
            # print(collection.get(ids=[idss]))
            # exit()
        # print([elem['doc_name'] for elem in collection.get(include=["metadatas"])])

if __name__ == "__main__":
    # main()
    clean_everything()
