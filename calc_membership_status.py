import copy
import csv
import argparse
import json



# Headers that will be carried through to output CSV(s)
passthrough_headers = ['Name', 'uniqname']

# The achievable levels of involvement. Key must match those in 'requirements' dict
achievable_classes = {
    'active': {},
    'da': {},
    'pa': {},
}

# The name of the entry containing service hours (for overflow calculations)
service_hours_entry_name = 'service';
# Default requirements for each member and class
requirements = {
    'total': {
        'column_title': 'Hours',
        'can_be_substituted_with_service': False,
        'active': 3,
        'da': 15,
        'pa': 33,
    },
    service_hours_entry_name: {
        'column_title': 'Service Hours',
        'can_be_substituted_with_service': False,
        'active': 2,
        'da': 11,
        'pa': 24,
    },
    'social_pd': {
        'column_title': 'Social/PD',
        'can_be_substituted_with_service': True,
        'active': 1,
        'da': 2,
        'pa': 2,
    },
    'electee_interviews': {
        'column_title': 'Conducted Interviews',
        'can_be_substituted_with_service': True,
        'active': 0,
        'da': 0.5,
        'pa': 0.5,
    },
    'voting_meeting_attendance': {
        'column_title': 'Voting Meeting Attendance',
        'can_be_substituted_with_service': True,
        'active': 0,
        'da': 3,
        'pa': 3,
        'nested_under': 'meeting_attendance',
    },
    'meeting_attendance': {
        'column_title': 'Voting Meeting Attendance',
        'can_be_substituted_with_service': True,
        'active': 0,
        'da': 5,
        'pa': 5,
    },
    'leadership_credit': {
        'column_title': 'Leadership',
        'can_be_substituted_with_service': False,
        'active': 0,
        'da': 1,
        'pa': 1,
    },
}

def main():
    ### PARSING
    parser = argparse.ArgumentParser(
        prog = 'calc_membership_status.py',
        description = 'Calculates Active/DA/PA Statuses from TBP website hours CSV. Outputs a file with delta values for each requirement',
    )

    parser.add_argument('input', type=open, help='input csv from TBP website to read from')
    parser.add_argument('output', type=argparse.FileType('w', encoding='UTF-8'), help='output csv to write delta values to')
    parser.add_argument('-c', '--config', type=open, help='supplied configuration for requirements')
    parser.add_argument('-p', '--preadjustment_out', type=argparse.FileType('w', encoding='UTF-8'), required=False, help='writes delta values before service-hours adjustment to csv')

    args = parser.parse_args()


    ### SETUP CSVs
    # If a different configuration was supplied, use that
    if args.config:
        requirements = json.load(args.config)

    # Reader/Writer
    csvReader = csv.DictReader(args.input)
    csvWriter = csv.writer(args.output)

    # If optional preadjustment data was requested, prepare writer
    preadjustWriter = None;
    if (args.preadjustment_out):
        preadjustWriter = csv.writer(args.preadjustment_out)

    # Prepare Headers
    header = copy.deepcopy(passthrough_headers)
    preadjust_header = copy.deepcopy(header)
    for class_key in achievable_classes:
        for req_key in requirements:
            header.append(class_key + "_" + req_key + "_delta")
            # preadjustment data
            preadjust_header.append(class_key + "_" + req_key + "_delta")
        header.append(class_key + "_status")

    # Write Headers
    csvWriter.writerow(header) 
    # preadjustment data
    if (args.preadjustment_out):
        preadjustWriter.writerow(header)     


    ### MEMBER LOOP
    for member in csvReader:
        member_progress_deltas = achievable_classes.copy();

        for req_key in requirements:
            req = requirements[req_key]
            completed_hours = member[req['column_title']]
            for class_key in achievable_classes:
                member_progress_deltas[class_key][req_key] = float(completed_hours) - req[class_key];

        # Service Hours Adjustment
        post_adjustment_member_progress_deltas = copy.deepcopy(member_progress_deltas);

        # Iterate over achievable classes
        for class_key in member_progress_deltas:
            achievable_class = member_progress_deltas[class_key]

            # Iterate over requirements
            for req_key in achievable_class:
                if requirements[req_key]["can_be_substituted_with_service"]:
                    delta = post_adjustment_member_progress_deltas[class_key][req_key]
                    if ((delta < 0) & (post_adjustment_member_progress_deltas[class_key][service_hours_entry_name] + delta >= 0)):
                        post_adjustment_member_progress_deltas[class_key][service_hours_entry_name] += delta
                        post_adjustment_member_progress_deltas[class_key][req_key] -= delta

                        if 'nested_under' in requirements[req_key]:
                            post_adjustment_member_progress_deltas[class_key][requirements[req_key]['nested_under']] -= delta

        # Holds delta data to be written to CSVs 
        output_data = [];

        # Write any passthrough data to the output
        for header_key in passthrough_headers:
            output_data.append(member[header_key]);
        
        # Create copy for preadjustment data
        preadjust_output_data = copy.deepcopy(output_data);

        for class_key in post_adjustment_member_progress_deltas:
            check_deltas(post_adjustment_member_progress_deltas[class_key], output_data)
            # Write preadjustment data
            if args.preadjustment_out:
                check_deltas(member_progress_deltas[class_key], preadjust_output_data)

        # Write data
        csvWriter.writerow(output_data) 
        # Write preadjustment data
        if args.preadjustment_out:
            preadjustWriter.writerow(preadjust_output_data);

def check_deltas(delta_dict, output_data):
  
    # Track missing requirements for a class
    missing_requirements = {}

    for req_key in delta_dict:
        val = delta_dict[req_key]

        # If any of the deltas remain below zero, that class is determeined unearned.
        if (val < 0):
            missing_requirements[req_key] = val

        # Write delta
        output_data.append(val)

    # If any requirements are missing, display them. Otherwise mark as earned.
    if missing_requirements:
        missing_string = "UNEARNED: "
        for req_key in missing_requirements:
            missing_string += req_key + ": " + str(missing_requirements[req_key]) + " | "

        output_data.append(missing_string)
    else:
        output_data.append("EARNED")

    return output_data

if __name__ == "__main__":
    main()



