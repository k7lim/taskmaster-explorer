#!/usr/bin/env python3
"""
Add wiki links and S/T task type tags to tasks-index-scored.json.

Cross-references task data against the Taskmaster fan wiki to:
1. Add wiki_task_url for each task's individual wiki page
2. Add wiki_series_url for each season's wiki page
3. Mark tasks tagged "S" (special/secret) or "T" (tiebreaker) on the wiki
"""

import json

# Wiki series URLs
WIKI_SERIES_URLS = {
    "s04": "https://taskmaster.fandom.com/wiki/Series_4",
    "s05": "https://taskmaster.fandom.com/wiki/Series_5",
    "s07": "https://taskmaster.fandom.com/wiki/Series_7",
    "nz-s02": "https://taskmaster.fandom.com/wiki/Season_2_(NZ)",
    "s19": "https://taskmaster.fandom.com/wiki/Series_19",
    "s20": "https://taskmaster.fandom.com/wiki/Series_20",
}

# Mapping of task IDs to wiki task page URLs and wiki type (S/T/None)
# Built by cross-referencing episode pages on taskmaster.fandom.com
WIKI_MAPPING = {
    'nz-s02-e01-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_green_thing_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e01-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Knock_over_all_the_pins_on_the_other_side_of_the_field_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e01-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Fly_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e01-t04': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Brush_Paul's_teeth_from_the_furthest_distance_(Taskmaster_NZ)", "wiki_type": None},
    'nz-s02-e01-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Build_the_tallest_tower_of_toilet_rolls_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e02-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Hottest_thing_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e02-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Float_this_brussels_sprout_down_from_the_balcony_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e02-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Transform_this_room_when_the_lights_go_out_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e02-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Squirt_the_sunscreen_the_furthest_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e02-t05': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Paint_a_portrait_of_Jeremy's_Mother_(Taskmaster_NZ)", "wiki_type": None},
    'nz-s02-e03-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_New_Zealand_thing_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e03-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Star_in_a_one-minute_multi-character_film_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e03-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Build_a_castle_out_of_wheat_biscuits_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e03-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Hop_the_scotch_along_the_hopscotch_and_pop_it_in_the_pail_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e03-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_a_photo_of_a_person_in_the_most_extraordinary_location_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e03-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Shake_the_coin_out_of_your_piggy_bank_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e04-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_impressive_stolen_item_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e04-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_the_swiss_ball_in_the_kayak_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e04-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Perform_an_original_Christmas_song_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e04-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Shoot_a_chocolate_fish_into_the_fishbowl_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e04-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Carry_a_briefcase_of_either_nothing_or_onions_across_the_stage_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e05-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_voucher_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e05-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Spill_the_beans_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e05-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_your_hometown_proud_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e05-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_loudest_noise_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e05-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Use_your_weapon_to_slice_your_snack_in_twain_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e06-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Two_most_different_things_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e06-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Evacuate_the_items_from_the_parachute_whilst_sitting_in_the_rocking_chair_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e06-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Create_a_diss_track_about_the_members_of_the_other_team_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e06-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Join_this_video_chat_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e06-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Taking_turns,_name_a_celebrity_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e07-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Biggest_bargain_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e07-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Construct_the_least_appropriate_wedding_cake_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e07-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Eat_the_grape_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e07-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_most_extreme_cup_of_tea_and_and_serve_it_to_Paul_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e07-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Survive_lemonade_roulette_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e08-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_nostalgia-inducing_item_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e08-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Build_a_tower_using_only_onions_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e08-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Time_travel_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e08-t04': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Pack_Paul's_car_with_inflated_objects_from_the_caravan_(Taskmaster_NZ)", "wiki_type": None},
    'nz-s02-e08-t04b': {"wiki_task_url": None, "wiki_type": None},
    'nz-s02-e08-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Draw_a_life-size_self-portrait_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e09-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_edible-looking_inedible_item_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e09-t02': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Steal_the_Taskmaster's_portrait_(Taskmaster_NZ)", "wiki_type": None},
    'nz-s02-e09-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Impale_your_umbrella_into_the_ground_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e09-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Take_Paul_on_the_perfect_first_date_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e09-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Re-enter_the_room_wearing_the_tie_in_a_brand_new_way_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e09-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Recreate_famous_scenes_from_NZ_history_for_the_Taskmaster_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e10-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_futuristic_thing_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e10-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_the_most_footage_of_Paul_on_this_camcorder_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e10-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Untie_these_shoelaces_(Taskmaster_NZ)', "wiki_type": 'S'},
    'nz-s02-e10-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Perform_an_educational_puppet_show_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e10-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Lift_the_two_milk_bottles_and_hover_them_directly_above_their_respective_microwaves_(Taskmaster_NZ)', "wiki_type": None},
    'nz-s02-e10-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Return_your_salad_items_to_their_original_order_(Taskmaster_NZ)', "wiki_type": None},
    's04-e01-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_interesting_autograph_on_the_most_interesting_vegetable', "wiki_type": None},
    's04-e01-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Destroy_this_cake', "wiki_type": None},
    's04-e01-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Create_the_best_caricature_of_the_person_on_the_other_side_of_the_curtain', "wiki_type": None},
    's04-e01-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Fell_all_the_rubber_ducks', "wiki_type": None},
    's04-e01-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_most_juice', "wiki_type": None},
    's04-e02-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_boastful_item', "wiki_type": None},
    's04-e02-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Keep_the_basketball_on_the_running_machine_for_as_long_as_possible', "wiki_type": None},
    's04-e02-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Paint_the_best_picture_of_the_Taskmaster', "wiki_type": None},
    's04-e02-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Land_the_flour_on_the_target', "wiki_type": None},
    's04-e02-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_the_egg_into_the_egg_cup', "wiki_type": None},
    's04-e02-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Attach_as_many_balloons_together_as_possible', "wiki_type": None},
    's04-e03-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_membership/subscription', "wiki_type": None},
    's04-e03-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Camouflage_yourself', "wiki_type": None},
    's04-e03-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_a_trailer_for_Taskmaster_The_Movie', "wiki_type": None},
    's04-e03-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Persuade_three_dogs_to_stand_on_the_red_mat', "wiki_type": None},
    's04-e03-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Transfer_the_water_from_fishbowl_A_to_fishbowl_B', "wiki_type": None},
    's04-e03-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Take_it_in_turns_to_say_a_5-letter_word_whenever_the_music_stops', "wiki_type": None},
    's04-e03-t07': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Decant_the_wine_into_another_bottle_from_atop_an_umpire's_chair", "wiki_type": 'T'},
    's04-e04-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_surprising_picture_of_themselves', "wiki_type": None},
    's04-e04-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_highest_splash', "wiki_type": None},
    's04-e04-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Choreograph_a_dance_for_you_and_Alex_to_perform_to_any_of_the_following_ringtones', "wiki_type": None},
    's04-e04-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Create_a_portrait_of_a_celebrity_using_loo_roll', "wiki_type": None},
    's04-e04-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Do_the_most_incredible_thing_with_this_pommel_horse', "wiki_type": None},
    's04-e04-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_highest_tower_using_these_tubes', "wiki_type": None},
    's04-e05-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Cutest_thing', "wiki_type": None},
    's04-e05-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Slide_the_furthest', "wiki_type": None},
    's04-e05-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Put_on_the_wetsuit,_flippers,_face_mask_and_snorkel', "wiki_type": None},
    's04-e05-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Put_as_many_different_things_in_the_bathtub/Seal_the_top_of_this_bathtub_with_cling_film', "wiki_type": None},
    's04-e05-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Throw_something_into_something', "wiki_type": None},
    's04-e05-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_longest_continuous_noise', "wiki_type": None},
    's04-e05-t07': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Eat_as_many_peas_as_possible', "wiki_type": 'T'},
    's04-e06-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_sheep-related_item', "wiki_type": None},
    's04-e06-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_this_camel_through_the_smallest_gap', "wiki_type": None},
    's04-e06-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Score_the_best_goal_with_this_plastic_bag', "wiki_type": None},
    's04-e06-t04': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Work_out_what's_in_the_sleeping_bag", "wiki_type": None},
    's04-e06-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Hold_all_your_items_in_one_hand', "wiki_type": None},
    's04-e07-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_chair', "wiki_type": None},
    's04-e07-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Bring_Alex_his_dinner', "wiki_type": None},
    's04-e07-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Hide_from_Alex', "wiki_type": None},
    's04-e07-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_this_wheelie_bin_across_the_finish_line', "wiki_type": None},
    's04-e07-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Unveil_a_new_handshake', "wiki_type": None},
    's04-e07-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_best_and_biggest_all-round_banana', "wiki_type": None},
    's04-e07-t07': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Open_this_jar', "wiki_type": 'T'},
    's04-e08-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_cash', "wiki_type": None},
    's04-e08-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_most_exotic_sandwich', "wiki_type": None},
    's04-e08-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Strike_one_of_these_objects_the_furthest_distance_with_one_of_the_other_objects', "wiki_type": None},
    's04-e08-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Do_something_surprising_with_this_rubber_duck', "wiki_type": None},
    's04-e08-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Draw_the_median_duck', "wiki_type": None},
    's05-e01-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Something_that_makes_the_most_excellent_noise', "wiki_type": None},
    's05-e01-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Give_Alex_a_special_cuddle', "wiki_type": None},
    's05-e01-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_Alex_onto_dry_land_as_elegantly_as_possible', "wiki_type": None},
    's05-e01-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_the_basketball_through_the_hoop', "wiki_type": None},
    's05-e01-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_one_item_of_fruit_into_the_fishbowl', "wiki_type": None},
    's05-e02-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Hippest_item_of_headwear', "wiki_type": None},
    's05-e02-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_best_coconut-flinging_machine', "wiki_type": None},
    's05-e02-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Paint_the_best_rainbow_scene', "wiki_type": None},
    's05-e02-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Slice_the_loaf_as_neatly_as_possible', "wiki_type": None},
    's05-e02-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Achieve_the_greatest_splat', "wiki_type": None},
    's05-e02-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Paint_the_most_recognisable_animal_vegetable_or_mineral', "wiki_type": None},
    's05-e03-t01': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/The_thing_they're_actually_proudest_of", "wiki_type": None},
    's05-e03-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Remove_the_table_tennis_ball_from_the_pipe', "wiki_type": None},
    's05-e03-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_this_coconut_look_like_a_businessman', "wiki_type": None},
    's05-e03-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Eat_one_item,_throw_one_item,_balance_one_item', "wiki_type": None},
    's05-e03-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Play_table_tennis_with_words', "wiki_type": None},
    's05-e04-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_extraordinary_souvenir', "wiki_type": None},
    's05-e04-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_marmite', "wiki_type": None},
    's05-e04-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Do_something_remarkable_synchronised', "wiki_type": None},
    's05-e04-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Spot_the_difference', "wiki_type": None},
    's05-e04-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Sneeze', "wiki_type": None},
    's05-e04-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Stand_on_one_leg_for_the_longest', "wiki_type": None},
    's05-e04-t07': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Back_throw_a_Swede', "wiki_type": 'T'},
    's05-e05-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_high-octane_item', "wiki_type": None},
    's05-e05-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Put_the_biggest_thing_inside_this_balloon', "wiki_type": None},
    's05-e05-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Generate_a_watercooler_moment_involving_this_water_cooler', "wiki_type": None},
    's05-e05-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Send_the_Taskmaster_an_anonymous_cheeky_text_message_every_single_day_for_the_next_five_months', "wiki_type": 'S'},
    's05-e05-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_tallest_tower_of_cans_on_this_table', "wiki_type": None},
    's05-e05-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Find_the_Finns', "wiki_type": None},
    's05-e06-t01': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Best_thing_they've_made_themselves", "wiki_type": None},
    's05-e06-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Balance_Alex', "wiki_type": None},
    's05-e06-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/With_this_camera_strapped_to_your_head,_record_the_most_incredible_footage', "wiki_type": None},
    's05-e06-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_the_most_yoghurt_near_the_middle_of_the_target_with_one_kick', "wiki_type": 'T'},
    's05-e06-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Have_your_photo_taken_with_this_golden_pineapple_in_other_esteemed_company', "wiki_type": 'S'},
    's05-e06-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Using_this_flame,_light_the_candle_in_the_caravan', "wiki_type": None},
    's05-e06-t07': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_yourself_monotone', "wiki_type": None},
    's05-e07-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_surprisingly_expensive_item', "wiki_type": None},
    's05-e07-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Wearing_that_blindfold_at_all_times,_travel_as_far_as_possible_in_three_minutes', "wiki_type": None},
    's05-e07-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Muster_the_biggest_coconut_bobsleigh_team', "wiki_type": None},
    's05-e07-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Vote_for_which_contestant_you_think_should_receive_five_bonus_points', "wiki_type": None},
    's05-e07-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_a_funny_little_flick-book_film', "wiki_type": None},
    's05-e07-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Send_the_most_things_to_the_Taskmaster', "wiki_type": None},
    's05-e08-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_awkward_item_for_somebody_else_to_take_home', "wiki_type": None},
    's05-e08-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_this_coconut_as_far_from_here_as_possible', "wiki_type": None},
    's05-e08-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Create_the_best_graph', "wiki_type": None},
    's05-e08-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_most_fish_puns', "wiki_type": 'S'},
    's05-e08-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Write_and_perform_a_song_about_this_woman', "wiki_type": None},
    's05-e08-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Throw_the_egg_through_the_hoop_and_catch_it_as_many_times_as_possible', "wiki_type": None},
    's07-e01-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/The_thing_that_most_people_would_like_to_touch', "wiki_type": None},
    's07-e01-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Design_and_demonstrate_the_best_quick-change_outfit', "wiki_type": None},
    's07-e01-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Build_the_highest_tower', "wiki_type": None},
    's07-e01-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Work_out_the_circumference_of_the_caravan_in_baked_beans', "wiki_type": None},
    's07-e01-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_best_fruit_display_hat', "wiki_type": None},
    's07-e02-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Boldest_belt', "wiki_type": None},
    's07-e02-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Write_a_ten-word_story_before_you_reach_the_finish_line', "wiki_type": None},
    's07-e02-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Paint_the_best_picture_of_this_still_life', "wiki_type": None},
    's07-e02-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Predict_what_another_contestant_will_do_with_one_of_the_objects', "wiki_type": None},
    's07-e02-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Draw_the_biggest_and_best_circle', "wiki_type": None},
    's07-e02-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_highest_tower_of_cans_within_your_hoop', "wiki_type": None},
    's07-e03-t01': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Best_thing_from_the_'90s", "wiki_type": None},
    's07-e03-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Excite_Alex', "wiki_type": None},
    's07-e03-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_best_noise', "wiki_type": None},
    's07-e03-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_this_ball_in_that_hole_in_as_few_strokes_as_possible', "wiki_type": None},
    's07-e03-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Write_down_a_ten-word_fact', "wiki_type": None},
    's07-e04-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_confusing_thing', "wiki_type": None},
    's07-e04-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Work_out_what_happens_when_you_flick_this_switch_on', "wiki_type": None},
    's07-e04-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Dramatically_alter_your_appearance', "wiki_type": None},
    's07-e04-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_these_scales_read_31.770kg', "wiki_type": None},
    's07-e04-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Correctly_don_the_most_items_of_clothing', "wiki_type": None},
    's07-e05-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Worst_present_from_a_named_relative', "wiki_type": None},
    's07-e05-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Deliver_this_task_to_Alex_in_the_most_spectacular_way', "wiki_type": None},
    's07-e05-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_as_many_white_circles_on_the_target_as_possible', "wiki_type": None},
    's07-e05-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Cheer_up_this_former_traffic_warden', "wiki_type": None},
    's07-e05-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_yourselves_look_as_little_or_big_as_possible', "wiki_type": None},
    's07-e05-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Dangle_one_of_these_items_on_the_hanger', "wiki_type": None},
    's07-e06-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_key', "wiki_type": None},
    's07-e06-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Put_exactly_50_different_things_in_this_bin', "wiki_type": None},
    's07-e06-t02b': {"wiki_task_url": None, "wiki_type": None},
    's07-e06-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Write_and_perform_the_most_suspenseful_soap_opera_cliff-hanger', "wiki_type": None},
    's07-e06-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Put_all_the_pairs_of_glasses_into_the_smallest_of_these_boxes', "wiki_type": None},
    's07-e06-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_your_doughnut_as_high_as_possible', "wiki_type": None},
    's07-e07-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_exciting_thing_beginning_with_G', "wiki_type": None},
    's07-e07-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Throw_something_into_the_bin_on_the_other_side_of_this_fence', "wiki_type": None},
    's07-e07-t03': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Don't_blink", "wiki_type": None},
    's07-e07-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_best_extension_to_the_Taskmaster_House', "wiki_type": None},
    's07-e07-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_best_Christmas_cracker', "wiki_type": None},
    's07-e07-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Walk_over_and_hit_that_drum_in_exactly_9.58_seconds', "wiki_type": None},
    's07-e08-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Creepiest_thing', "wiki_type": None},
    's07-e08-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Poke_something_out_of_the_hole_in_the_roof_of_this_grotto', "wiki_type": None},
    's07-e08-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Scream', "wiki_type": None},
    's07-e08-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Compose_the_best_30_second_piece_of_music', "wiki_type": None},
    's07-e08-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Bob_when_you_hear_the_surname_of_a_famous_Bob', "wiki_type": None},
    's07-e09-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_surprisingly_beautiful_thing', "wiki_type": None},
    's07-e09-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Put_the_most_money_in_the_small_bowl', "wiki_type": None},
    's07-e09-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Be_photographed_in_the_most_unusual_situation_wearing_this_fez', "wiki_type": None},
    's07-e09-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Hula', "wiki_type": None},
    's07-e09-t04b': {"wiki_task_url": None, "wiki_type": None},
    's07-e09-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Find_the_sock_with_a_satsuma_inside', "wiki_type": None},
    's07-e09-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Achieve_a_rally_of_exactly_24_shots', "wiki_type": None},
    's07-e09-t07': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Write_your_name_and_draw_a_picture_of_a_happy_horse', "wiki_type": None},
    's07-e10-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_magnificent_stationery', "wiki_type": None},
    's07-e10-t01b': {"wiki_task_url": None, "wiki_type": None},
    's07-e10-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Find_the_boiled_egg', "wiki_type": None},
    's07-e10-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Physically_recreate_a_classic_computer_game', "wiki_type": None},
    's07-e10-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Tie_yourself_up_as_securely_as_possible', "wiki_type": None},
    's07-e10-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Prod_the_person_in_front_of_you_with_either_a_finger_or_a_sausage', "wiki_type": None},
    's19-e01-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/The_object_that_reminds_you_of_school_the_most_in_a_good_way', "wiki_type": None},
    's19-e01-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Pour_all_the_vinegar_into_the_fish_tank', "wiki_type": None},
    's19-e01-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Do_your_cool_thing_backwards', "wiki_type": None},
    's19-e01-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Win_the_Pealympics', "wiki_type": None},
    's19-e01-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_the_most_raisins_in_your_wine_glass', "wiki_type": None},
    's19-e02-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Snootiest_thing', "wiki_type": None},
    's19-e02-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Commentate_on_yourself_achieving_something_really_tricky,_then_achieve_that_really_tricky_thing', "wiki_type": None},
    's19-e02-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Give_Alex_exactly_100_marbles_on_a_plate_and_an_eggcup_full_of_tepid_water', "wiki_type": None},
    's19-e02-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_the_most_liquid_in_this_can', "wiki_type": None},
    's19-e02-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Put_one_of_your_items_completely_inside_the_other_item', "wiki_type": None},
    's19-e03-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_thing_for_a_middle-aged_man_to_keep_on_his_bedside_table', "wiki_type": None},
    's19-e03-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Answer_the_cheese_phone', "wiki_type": None},
    's19-e03-t03': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Move_the_most_cushions_from_one_bin_to_the_other_bin_without_Alex_correctly_saying_what_colour_cape_you're_wearing", "wiki_type": None},
    's19-e03-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Paint_the_best_picture_of_the_Taskmaster_and_his_assistant_having_fun_on_the_canvas_in_the_lab', "wiki_type": None},
    's19-e03-t05': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Take_it_in_turns_as_teams_to_obey_Greg's_previous_order", "wiki_type": None},
    's19-e04-t01': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/The_thing_that_least_suits_its_name_if_you_shout_it_loudly_while_we're_all_looking_at_it_on_the_screen", "wiki_type": None},
    's19-e04-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Put_the_most_wetsuits_on_mannequins', "wiki_type": None},
    's19-e04-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Convince_the_other_team_that_the_following_things_are_the_opposite_of_what_they_are', "wiki_type": None},
    's19-e04-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Tell_Alex_why_the_light_bulb_turns_on', "wiki_type": None},
    's19-e04-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Win_a_game_of_Front_Ham', "wiki_type": None},
    's19-e05-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_object_to_bestow_in_your_will_to_a_relative_against_whom_you_are_seeking_revenge', "wiki_type": None},
    's19-e05-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Be_the_least_annoying_person_round_the_campfire', "wiki_type": None},
    's19-e05-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Draw_the_monster', "wiki_type": None},
    's19-e05-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Write_down_every_word_you_said_in_this_room_before_you_opened_this_task', "wiki_type": None},
    's19-e05-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Pop_a_balloon_when_you_hear_its_colour', "wiki_type": None},
    's19-e05-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_as_many_holes_in_this_sheet_of_paper_as_possible', "wiki_type": 'T'},
    's19-e06-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/The_thing_that_is_nicest_to_open', "wiki_type": None},
    's19-e06-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Work_out_what_Alex_has_on_the_very_top_of_his_head', "wiki_type": None},
    's19-e06-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Capture_your_relationship_with_a_classic_family_home_video_moment', "wiki_type": None},
    's19-e06-t04': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Teach_the_Taskmaster's_Assistant_a_lesson_he'll_never_forget", "wiki_type": None},
    's19-e06-t05': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Don't_blow_the_last_thing_off_the_table", "wiki_type": None},
    's19-e07-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Biggest_anticlimax', "wiki_type": None},
    's19-e07-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/What_is_in_the_one_yellow_box%3F', "wiki_type": None},
    's19-e07-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Eat_this_yoghurt_with_the_most/least_dignity', "wiki_type": None},
    's19-e07-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Put_at_least_six_litres_of_water_in_the_vase', "wiki_type": None},
    's19-e07-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_one_of_your_balls_into_your_bucket', "wiki_type": None},
    's19-e08-t01': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Best_object_that_you've_borrowed_from_a_fairly_close_friend", "wiki_type": None},
    's19-e08-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Fail_the_next_task_in_the_most_heartbreakingly_spectacular_way', "wiki_type": None},
    's19-e08-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Paint_your_memorable_scene_so_that_your_teammates_can_guess_your_three_words', "wiki_type": None},
    's19-e08-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Obey_the_autocue', "wiki_type": None},
    's19-e08-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Say_whether_the_next_person_will_have_a_higher_or_lower_number_of_things_than_the_previous_person', "wiki_type": None},
    's19-e09-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_satisfying_thing_you_could_use_as_a_jelly_mould', "wiki_type": None},
    's19-e09-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Place_something_somewhere_surprising', "wiki_type": None},
    's19-e09-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Create_the_most_exciting_new_bodies_so_that_you_and_Alex_become_a_dynamic_duo', "wiki_type": None},
    's19-e09-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Conquer_the_multitask', "wiki_type": None},
    's19-e09-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Say_a_word_that_fits_the_category_given_by_the_Taskmaster,_then_press_your_button', "wiki_type": None},
    's19-e10-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/The_thing_most_likely_to_make_you_do_a_double-take', "wiki_type": None},
    's19-e10-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Completely_fill_the_yellow_box_with_sand', "wiki_type": None},
    's19-e10-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Stay_completely_still_in_your_powerful_pose', "wiki_type": None},
    's19-e10-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Provide_the_best_drive-through_experience', "wiki_type": None},
    's19-e10-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_the_most_carrot_in_your_bucket', "wiki_type": None},
    's20-e01-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/A_very_soft_thing_which_would_be_most_beneficial_for_Greg_Davies', "wiki_type": None},
    's20-e01-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Honk_the_horn', "wiki_type": None},
    's20-e01-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Roll_an_object_onto_the_target', "wiki_type": None},
    's20-e01-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Do_something_behind_this_curtain_that_sounds_disgusting_but_is_actually_really_nice', "wiki_type": None},
    's20-e01-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/End_up_on_your_spot', "wiki_type": None},
    's20-e02-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/The_object_that_is_hardest_to_describe', "wiki_type": None},
    's20-e02-t02': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Identify_Alex's_five_things", "wiki_type": None},
    's20-e02-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Remove_the_most_flour_from_the_tray_without_touching_flour_with_your_hands', "wiki_type": None},
    's20-e02-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Take_the_most_surprising_thing_out_of_this_bag', "wiki_type": None},
    's20-e02-t05': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Guess_how_many_things_the_Taskmaster's_assistant_has_on_him", "wiki_type": None},
    's20-e03-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/The_thing_you_were_least_likely_to_bring_in_from_your_home', "wiki_type": None},
    's20-e03-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_most_accurate_little_model_of_the_Chesham_United_mascot', "wiki_type": None},
    's20-e03-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Discover_the_name_of_the_person_in_the_lab', "wiki_type": None},
    's20-e03-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Win_Snakes_and_Steps', "wiki_type": None},
    's20-e03-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Turn_your_cup_triangle_completely_upside_down', "wiki_type": None},
    's20-e04-t01': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/The_present_that_would_most_make_you_say_this_if_you_received_it_on_your_birthday:_%22Oh,_that's_just_the_most_gorgeous_gift_ever!%22", "wiki_type": None},
    's20-e04-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/What_number_has_Alex_written_down%3F', "wiki_type": None},
    's20-e04-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_a_love_heart_using_your_body,_the_body_of_your_teammates_and_any_other_items_of_your_choosing', "wiki_type": None},
    's20-e04-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Win_the_horse_race', "wiki_type": None},
    's20-e04-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Either_convince_the_Taskmaster_you_have_written_something_other_than_what_you_have_written_or_exactly_what_you_have_written', "wiki_type": None},
    's20-e04-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Remove_your_shower_cap_by_inflating_the_balloon', "wiki_type": 'T'},
    's20-e05-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/A_possession_that_would_most_confuse_a_future_archaeologist_if_you_were_buried_holding_it', "wiki_type": None},
    's20-e05-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Pull_something_from_that_red_green_onto_this_red_green_using_this_string', "wiki_type": None},
    's20-e05-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_things_genuinely_awkward', "wiki_type": None},
    's20-e05-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Do_the_most_accurate_finger_painting_of_the_person_on_the_other_end_of_the_phone', "wiki_type": None},
    's20-e05-t05': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Eat_the_lam%C3%A9_duck_or_don't_eat_the_lam%C3%A9_duck", "wiki_type": None},
    's20-e06-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/The_thing_Greg_would_most_like_to_see_Alex_wearing', "wiki_type": None},
    's20-e06-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Cut_a_single_string_to_cause_the_greatest_effect', "wiki_type": None},
    's20-e06-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Communicate_your_story_to_the_Taskmaster', "wiki_type": None},
    's20-e06-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Wear_the_flippers_correctly', "wiki_type": None},
    's20-e06-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Find_the_age_of_the_mystery_person', "wiki_type": None},
    's20-e07-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_thing_you_can_either_ride_or_rip', "wiki_type": None},
    's20-e07-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Steal_the_statue_of_Archimedes', "wiki_type": None},
    's20-e07-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Dribble_a_technicolour_picture_of_your_hero', "wiki_type": None},
    's20-e07-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Get_exactly_63_points_by_bopping_Alex_on_the_head', "wiki_type": None},
    's20-e07-t05': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Avoid_the_Taskmaster's_big_ball", "wiki_type": None},
    's20-e08-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_thing_that_has_a_surprise_aspect_to_it', "wiki_type": None},
    's20-e08-t02': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Go_and_sit_in_the_entrance_lobby_on_Alex's_horn_and_return_on_Alex's_whistle", "wiki_type": None},
    's20-e08-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Paint_the_best_picture_of_one_animal_sitting_on_top_of_another_animal', "wiki_type": None},
    's20-e08-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Say_the_most_five-letter_words', "wiki_type": None},
    's20-e08-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Demonstrate_to_the_Taskmaster_the_idiom_demonstrated_to_you_by_your_teammate', "wiki_type": None},
    's20-e09-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Most_respected_item_that_retains_its_credibility_when_you_talk_about_it_in_a_high-pitched_voice', "wiki_type": None},
    's20-e09-t02': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Build_a_tower_of_bricks_on_this_trolley,_then_push_it_down_the_slope', "wiki_type": None},
    's20-e09-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_your_jockey_weigh_almost_exactly_the_same_as_Alex', "wiki_type": None},
    's20-e09-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_the_most_fantastic_15-second_film_featuring_your_face_in_full_frame', "wiki_type": None},
    's20-e09-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Become_the_person_the_Taskmaster_shouts', "wiki_type": None},
    's20-e10-t01': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Best_tube', "wiki_type": None},
    's20-e10-t02': {"wiki_task_url": "https://taskmaster.fandom.com/wiki/Make_exactly_the_same-looking_drinks_as_your_teammate's_drinks", "wiki_type": None},
    's20-e10-t03': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Drink_almost_all_the_apple_juice', "wiki_type": None},
    's20-e10-t04': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Make_water_squirt_out_of_you_in_a_surprising_way', "wiki_type": None},
    's20-e10-t05': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/Respond_to_the_Taskmaster_correctly', "wiki_type": None},
    's20-e10-t06': {"wiki_task_url": 'https://taskmaster.fandom.com/wiki/How_many_letter_Ts_are_there_in_the_portrait_of_Alex_and_Greg_in_the_living_room%3F', "wiki_type": 'T'},
}


def main():
    input_file = "tasks-index-scored.json"

    with open(input_file) as f:
        tasks = json.load(f)

    s_tasks = []
    t_tasks = []
    urls_added = 0
    series_urls_added = 0
    type_changes = 0

    for task in tasks:
        tid = task["id"]
        season = task["season"]

        # Add wiki_series_url
        if season in WIKI_SERIES_URLS:
            task["wiki_series_url"] = WIKI_SERIES_URLS[season]
            series_urls_added += 1

        # Add wiki_task_url and update task_type for S/T
        if tid in WIKI_MAPPING:
            info = WIKI_MAPPING[tid]
            task["wiki_task_url"] = info["wiki_task_url"]
            if info["wiki_task_url"]:
                urls_added += 1

            if info["wiki_type"] == "S":
                if task["task_type"] != "special":
                    print(f"  TYPE CHANGE: {tid} '{task['task_type']}' -> 'special' (wiki: S)")
                    type_changes += 1
                task["task_type"] = "special"
                s_tasks.append(tid)
            elif info["wiki_type"] == "T":
                if task["task_type"] != "special":
                    print(f"  TYPE CHANGE: {tid} '{task['task_type']}' -> 'special' (wiki: T)")
                    type_changes += 1
                task["task_type"] = "special"
                t_tasks.append(tid)
        else:
            task["wiki_task_url"] = None
            print(f"  WARNING: No wiki mapping for {tid}")

    with open(input_file, "w") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total tasks processed: {len(tasks)}")
    print(f"Wiki task URLs added:  {urls_added}")
    print(f"Wiki task URLs null:   {len(tasks) - urls_added} (sub-tasks without own wiki page)")
    print(f"Wiki series URLs added: {series_urls_added}")
    print(f"Task type changes:     {type_changes}")
    print(f"\nS (special/secret) tasks found on wiki ({len(s_tasks)}):")
    for tid in s_tasks:
        t = next(tt for tt in tasks if tt["id"] == tid)
        print(f"  {tid}: {t['task_description'][:80]}")
    print(f"\nT (tiebreaker) tasks found on wiki ({len(t_tasks)}):")
    for tid in t_tasks:
        t = next(tt for tt in tasks if tt["id"] == tid)
        print(f"  {tid}: {t['task_description'][:80]}")
    print(f"\nNote: Wiki also lists S/T tasks not in our data:")
    print(f"  S4 ep6: 'Hide this ball from Alex' (S) - not in our index")
    print(f"  S7 ep2: 'What number is written on Alex's left forearm?' (T) - not in our index")
    print(f"  S7 ep4: 'Make the best loo roll paper airplane' (T) - not in our index")
    print(f"  S19 ep3: 'Wear the magic moustache' (S) - not in our index")
    print(f"  S19 ep4: 'Read this out loud and in full' (S) - not in our index")
    print(f"  S19 ep9: 'Wear the magic moustache' (S) - not in our index")


if __name__ == "__main__":
    main()
