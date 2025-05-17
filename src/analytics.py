# src/analytics.py
def assign_position_group(position):
    position_groups = {
        'GOALKEEPER': ['GK'],
        'DEFENSIVE': ['CB', 'LB', 'RB', 'FB', 'LWB', 'RWB', 'SW', 'D'],
        'MIDFIELD': ['CM', 'DM', 'MF', 'AM'],
        'ATTACKING': ['CF', 'ST', 'F', 'FW', 'LW', 'RW', 'WF', 'IF', 'OL', 'OR']
    }
    for group, codes in position_groups.items():
        if any(code in position for code in codes):
            return group
    return "UNKNOWN"


def calculate_rating_per_90(row):
    score = (
        row['Goals'] * 5 +
        row['Assists'] * 4 +
        row['Shots_on_target'] * 0.5 +
        (row['Shots'] - row['Shots_on_target']) * 0.1 -
        row['Yellow_cards'] * 1 -
        row['Red_cards'] * 2
    )
    return score / (row['Minutes'] / 90) if row['Minutes'] > 0 else 0
