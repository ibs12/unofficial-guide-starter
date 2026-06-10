# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

**Off-campus housing for NYU students in New York City** — neighborhood selection (Astoria, Williamsburg, the East Village, the Lower East Side, Washington Heights, Ridgewood), lease mechanics, guarantors, scams, and tenant rights. Useful because NYU's official housing resources cover lease and legal mechanics well but say nothing about what it's actually like to live in a given neighborhood, while that lived experience exists on Reddit but is scattered across hundreds of threads with conflicting opinions and no synthesis.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|------|-----------------|
| 1 | r/AskNYC — Astoria: stupid to give up $2400 rent? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1nxt34s/is_it_stupid_to_give_up_our_2400_rent_in_astoria/ |
| 2 | r/AskNYC — Questions about living in Astoria | Reddit thread | https://www.reddit.com/r/AskNYC/comments/13m2suz/questions_about_living_in_astoria/ |
| 3 | r/AskNYC — Why is Astoria so cheap? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/16ea3ox/why_is_astoria_so_cheap/ |
| 4 | r/AskNYC — Advice: should I live in Astoria? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1ck9b1k/adice_should_i_live_in_astoria/ |
| 5 | r/AskNYC — Williamsburg or Astoria? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/sx1gab/williamsburg_or_astoria/ |
| 6 | r/AskNYC — What neighborhoods should I consider living in? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/9q5ba0/what_neighborhoods_should_i_consider_living_in/ |
| 7 | r/AskNYC — East Village: anywhere I should avoid living? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1eqs236/is_there_anywhere_i_should_avoid_living_in_the/ |
| 8 | r/AskNYC — Safety concerns living in a street-facing 2nd floor | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1fvvek7/safety_concerns_living_in_a_streetfacing_2nd/ |
| 9 | r/AskNYC — Is the East Village experience enjoyable? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/og2bu6/is_the_east_village_experience_enjoyable_if/ |
| 10 | r/AskNYC — Are there bad areas to live in the East Village? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/mu4lrl/are_there_bad_areas_to_live_in_the_east_village/ |
| 11 | r/AskNYC — Why is Washington Heights so cheap compared to rest of Manhattan? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/x2sulr/why_is_washington_heights_so_cheap_compared_to/ |
| 12 | r/AskNYC — What are Washington Heights / Hamilton Heights like? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1ap95g2/what_are_washington_heights_hamilton_heights/ |
| 13 | r/AskNYC — How safe is Washington Heights from around 161st St? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1e419hr/how_safe_is_washington_heights_from_around_161st/ |
| 14 | r/AskNYC — Anyone have positive/negative opinions on their neighborhood? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1s83226/anyone_have_positivenegative_opinions_on_their/ |
| 15 | r/AskNYC — Washington Heights favorites | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1s9mohx/washington_heights_favorites/ |
| 16 | r/AskNYC — Followed 45 blocks in the LES | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1o9bqsv/followed_45_blocks_in_the_les/ |
| 17 | r/AskNYC — Living in LES | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1fjtusp/living_in_les/ |
| 18 | r/AskNYC — How is the LES these days? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/xoi5jk/how_is_the_les_these_days/ |
| 19 | r/AskNYC — LES in your 30s | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1b3kn4y/les_in_your_30s/ |
| 20 | r/AskNYC — What's the deal with cancer in Greenpoint? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1k22wlj/whats_the_deal_with_cancer_in_greenpoint/ |
| 21 | r/AskNYC — Help me decide between these three neighborhoods | Reddit thread | https://www.reddit.com/r/AskNYC/comments/1j23bbv/help_me_decide_between_these_three_neighborhoods/ |
| 22 | r/AskNYC — Is Ridgewood a good option for a college student? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/ewitl2/is_ridgewood_a_good_option_for_college_student/ |
| 23 | r/AskNYC — Why is Ridgewood trendy? | Reddit thread | https://www.reddit.com/r/AskNYC/comments/xgramv/why_is_ridgewood_trendy/ |
| 24 | r/nyu — How hard is it to live off campus? | Reddit thread | https://www.reddit.com/r/nyu/comments/1ibva9c/how_hard_is_it_to_live_off_campus/ |
| 25 | r/nyu — People living off-campus, how long before the start? | Reddit thread | https://www.reddit.com/r/nyu/comments/o1r94w/people_living_offcampus_how_long_before_the_start/ |
| 26 | r/nyu — Please break it down for an out-of-state student | Reddit thread | https://www.reddit.com/r/nyu/comments/1toovnb/please_break_it_down_for_an_out_of_state_student/ |
| 27 | r/nyu — To all my Indian brethren, here's how I found housing | Reddit thread | https://www.reddit.com/r/nyu/comments/144ok05/to_all_my_indian_brethren_out_there_this_is_how_i/ |
| 28 | r/nyu — Legal matters for off-campus housing in NYC | Reddit thread | https://www.reddit.com/r/nyu/comments/njbx3a/legal_matters_for_offcampus_housing_in_nyc/ |
| 29 | r/NYCapartments — How regular New Yorkers get apartments | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1n9c4dh/this_is_how_regular_new_yorkers_get_apartments/ |
| 30 | r/NYCapartments — How I found my NYC apartment in May 2026 (post-FARE) | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1synk84/how_i_found_my_nyc_apartment_in_may_2026_postfare/ |
| 31 | r/NYCapartments — Advice for NYC apartment seekers | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1efhsj0/i_have_some_advice_for_nyc_apartment_seekers/ |
| 32 | r/NYCapartments — How I found my dream NYC apartment | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1nzb1of/how_i_found_my_dream_nyc_apartment/ |
| 33 | r/NYCapartments — I built a free tool for renters to spot scams | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1tyhs50/i_built_a_free_tool_for_renters_to_easily_spot/ |
| 34 | r/NYCapartments — List of all the different apartment-hunting websites | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1k24otl/i_created_a_list_of_all_the_different_websites/ |
| 35 | r/NYCapartments — These income requirements are killing me | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1tlo2ve/these_income_requirements_are_killing_me/ |
| 36 | r/NYCapartments — Is it me or did the rentpocalypse just start? | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1ju49pq/is_it_me_or_did_the_rentpocalypse_just_start/ |
| 37 | r/NYCapartments — FARE Act passed | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1gqm8ui/fare_act_passed/ |
| 38 | r/NYCapartments — StreetEasy has become almost completely useless | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1s2we9l/streeteasy_has_become_almost_completely_useless/ |
| 39 | r/NYCapartments — No, you do not need to make $200k to live here | Reddit thread | https://www.reddit.com/r/NYCapartments/comments/1hv06v5/no_you_do_not_need_to_be_making_200k_to_live_here/ |
| 40 | r/movingtoNYC — Things I wish I knew about apartment hunting | Reddit thread | https://www.reddit.com/r/movingtoNYC/comments/1tq6h95/things_i_wish_i_knew_about_apartment_hunting/ |
| 41 | r/movingtoNYC — How are people affording $4k 1BR apartments? | Reddit thread | https://www.reddit.com/r/movingtoNYC/comments/1n8jqf7/how_are_people_affording_4k_1bdrm_apartments_in/ |
| 42 | r/movingtoNYC — Ultimate Renting 202 thread | Reddit thread | https://www.reddit.com/r/movingtoNYC/comments/1jae3ea/ultimate_renting_202_thread/ |
| 43 | r/movingtoNYC — FYI the FARE Act has taken effect | Reddit thread | https://www.reddit.com/r/movingtoNYC/comments/1lag03q/fyi_the_fare_act_has_taken_effect_landlords_can/ |
| 44 | NYU Off-Campus Housing — Avoiding Rental Scams | PDF (official guide) | https://offcampushousing.nyu.edu/resources/article/3408-avoiding-rental-scams |
| 45 | NYU Off-Campus Housing — Be a Good Neighbor | PDF (official guide) | https://offcampushousing.nyu.edu/resources/article/3879-be-a-good-neighbor |
| 46 | NYU Off-Campus Housing — Common Apartment Rental Terms | PDF (official guide) | https://offcampushousing.nyu.edu/resources/article/3466-common-apartment-rental-terms |
| 47 | NYU Off-Campus Housing — Common Lease Terms | PDF (official guide) | https://offcampushousing.nyu.edu/resources/article/3469-common-lease-terms |
| 48 | NYU Off-Campus Housing — Costs and Budgeting | PDF (official guide) | https://offcampushousing.nyu.edu/resources/article/3464-costs-and-budgeting |
| 49 | NYU Off-Campus Housing — Lease Guarantor | PDF (official guide) | https://offcampushousing.nyu.edu/resources/article/3468-lease-guarantor |
| 50 | NYU Off-Campus Housing — Living with Roommates | PDF (official guide) | https://offcampushousing.nyu.edu/resources/article/3463-living-with-roommates |
| 51 | NYU Off-Campus Housing — New York City Legal Assistance | PDF (official guide) | https://offcampushousing.nyu.edu/resources/article/3461-new-york-city-legal-assistance |
| 52 | NYU Off-Campus Housing — Transportation | PDF (official guide) | https://offcampushousing.nyu.edu/resources/article/3465-transportation |
| 53 | NY State Attorney General — Residential Tenants' Rights Guide | PDF (government guide) | documents/nyu_official/residential_tenants_rights_guide_ny_ag.pdf |
| 54 | NY State Attorney General — Publications Library | PDF (government guide) | documents/nyu_official/ny_ag_publications_library.pdf |
| 55 | NYC HPD — Tenant Rights and Responsibilities | PDF (government guide) | documents/nyu_official/tenant_rights_and_responsibilities_hpd.pdf |
| 56 | City of Jersey City — Landlord/Tenant Relations | PDF (government guide) | documents/nyu_official/landlord_tenant_relations_jersey_city.pdf |
| 57 | NJ Department of Community Affairs | PDF (government guide) | documents/nyu_official/nj_dept_community_affairs.pdf |
| 58 | Rent Leveling and Stabilization (NJ municipal ordinance) | PDF (government guide) | documents/nyu_official/rent_leveling_and_stabilization.pdf |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
