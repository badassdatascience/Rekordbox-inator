
#
# load useful libraries
#
import pandas as pd

#
# Parse track dictionary into a Pandas dataframe
#
class rkb_parsed_xml_list_per_track():
    
    def __init__(self, track_dict, track_id):

        # initialize class attributes
        self.track_dict = track_dict
        self.track_id = track_id
        self.parsed_list = []
        
        # retrieve the list from the XML
        if self.field_name in self.track_dict:
            self.parsed_list = self.track_dict[self.field_name]
        
        # sometimes the XML returns a string for certain nodes, ensure we have a list
        if str(type(self.parsed_list)) != "<class 'list'>":
            self.parsed_list = [self.parsed_list]

        # remove the '@' at the beginning of each dictionary key
        self.parsed_list = [{ k.replace('@', ''): v for k, v in x.items() } for x in self.parsed_list]
        
        # create per-track dataframe and add its ID
        self.df = pd.DataFrame(self.parsed_list)
        self.df['TrackID'] = track_id
        
#
# separate out the tempo information and express in a different Pandas dataframe
# linked to the above-computed dataframe by "TrackID"
#
class rkb_parsed_tempo_list_per_track(rkb_parsed_xml_list_per_track):
    def __init__(self, track_dict, track_id):
        self.field_name = 'TEMPO'
        super().__init__(track_dict, track_id)
        
        numeric_columns = ['Bpm', 'Battito', 'Inizio']

        for column in numeric_columns:
            if column in self.df.columns:
                self.df[column] = pd.to_numeric(self.df[column])
        
#
# separate out the cue position information and express in a different Pandas dataframe
# linked to the above-computed dataframe by "TrackID"
#
class rkb_parsed_cue_position_list_per_track(rkb_parsed_xml_list_per_track):
    def __init__(self, track_dict, track_id):
        self.field_name = 'POSITION_MARK'
        super().__init__(track_dict, track_id)
        
        numeric_columns = [
            'Type', 'Start', 'End', 'Num', 'Red', 'Green', 'Blue']

        for column in numeric_columns:
            if column in self.df.columns:
                self.df[column] = pd.to_numeric(self.df[column])
            
#
# class for representing a given track
#
class rkb_track():
    def __init__(self, track_dict):
        columns = [x for x in track_dict.keys() if not x in ['TEMPO', 'POSITION_MARK']]
        self.track_dict = { k.replace('@', ''): v for k, v in track_dict.items() if k in columns}
        
        numeric_columns = [
            'TrackID',
            'Size',
            'TotalTime',
            'BitRate',
            'SampleRate',
            'PlayCount',
            'Rating',
            'AverageBpm',
            'DiscNumber',
            'TrackNumber',
            'Year',
        ]
        
        for column in numeric_columns:
            self.track_dict[column] = pd.to_numeric(self.track_dict[column])
        
        track_id = self.track_dict['TrackID']
        
        self.tempo = rkb_parsed_tempo_list_per_track(track_dict, track_id)
        self.cue_position = rkb_parsed_cue_position_list_per_track(track_dict, track_id)

#
# class for representing all classes in the Rekordbox collection
#
class rkb_all_tracks():

    def __init__(self, dict_content, track_id_list = None):
        dict_list_track_info = []
        df_list_parsed_tempo = []
        df_list_parsed_cue_position = []
        for track_dict in dict_content['DJ_PLAYLISTS']['COLLECTION']['TRACK']:
    
            if track_id_list != None:
                if not track_dict['@TrackID'] in track_id_list:
                    continue

            track_info = rkb_track(track_dict)
    
            dict_list_track_info.append(track_info.track_dict)
            df_list_parsed_tempo.append(track_info.tempo.df)
            df_list_parsed_cue_position.append(track_info.cue_position.df)

        self.df_track_info = pd.DataFrame(dict_list_track_info)
        self.df_all_tempo = pd.concat(df_list_parsed_tempo)
        self.df_all_cue_positions = pd.concat(df_list_parsed_cue_position)