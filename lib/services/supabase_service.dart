import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/fighter.dart';
import '../models/fight.dart';
import '../models/event.dart';
import '../models/user.dart' as app_user;

class SupabaseService {
  static SupabaseService? _instance;
  static SupabaseService get instance => _instance ??= SupabaseService._();
  
  late final SupabaseClient _client;
  
  SupabaseService._() {
    _client = Supabase.instance.client;
  }

  // Note: Authentication is handled by Clerk.dev, not Supabase
  // This service focuses only on database operations

  // Fighters
  Future<List<Fighter>> getFighters({
    String? weightClass,
    bool activeOnly = true,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final response = await _client
          .from('fighters')
          .select()
          .limit(limit)
          .range(offset, offset + limit - 1);
      
      return response.map((json) => Fighter.fromJson(json)).toList();
    } catch (e) {
      print('Error getting fighters: $e');
      return [];
    }
  }

  Future<Fighter?> getFighter(String id) async {
    try {
      final response = await _client
          .from('fighters')
          .select()
          .eq('id', id)
          .maybeSingle();
      
      return response != null ? Fighter.fromJson(response) : null;
    } catch (e) {
      print('Error getting fighter: $e');
      return null;
    }
  }

  Future<List<String>> getWeightClasses() async {
    try {
      final response = await _client
          .from('fighters')
          .select('weight_class');
      
      return response
          .map((row) => row['weight_class'] as String?)
          .where((weightClass) => weightClass != null)
          .map((weightClass) => weightClass!)
          .toSet()
          .toList();
    } catch (e) {
      print('Error getting weight classes: $e');
      return [];
    }
  }

  Future<List<Fighter>> searchFighters(String query) async {
    try {
      final response = await _client
          .from('fighters')
          .select()
          .limit(20);
      
      return response
          .map((json) => Fighter.fromJson(json))
          .where((fighter) => 
              fighter.name.toLowerCase().contains(query.toLowerCase()) ||
              (fighter.nickname?.toLowerCase().contains(query.toLowerCase()) ?? false))
          .toList();
    } catch (e) {
      print('Error searching fighters: $e');
      return [];
    }
  }

  // Rankings
  Future<List<Fighter>> getRankings(String weightClass) async {
    try {
      final response = await _client
          .from('rankings')
          .select('*, fighters(*)')
          .eq('weight_class', weightClass);
      
      return response.map((json) {
        final fighterData = json['fighters'] as Map<String, dynamic>?;
        return fighterData != null ? Fighter.fromJson(fighterData) : null;
      }).where((fighter) => fighter != null).map((fighter) => fighter!).toList();
    } catch (e) {
      print('Error getting rankings: $e');
      return [];
    }
  }

  // Fights
  Future<List<Fight>> getFights({
    bool upcoming = true,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      // First get all fights
      final response = await _client
          .from('fights')
          .select('*')
          .limit(limit)
          .range(offset, offset + limit - 1);
      
      List<Fight> fights = [];
      
      // For each fight, get the fighter details separately
      for (var fightJson in response) {
        try {
          // Get fighter1 details
          Fighter? fighter1;
          if (fightJson['fighter1_id'] != null) {
            final fighter1Response = await _client
                .from('fighters')
                .select('*')
                .eq('id', fightJson['fighter1_id'])
                .maybeSingle();
            
            if (fighter1Response != null) {
              fighter1 = Fighter.fromJson(fighter1Response);
            }
          }
          
          // Get fighter2 details
          Fighter? fighter2;
          if (fightJson['fighter2_id'] != null) {
            final fighter2Response = await _client
                .from('fighters')
                .select('*')
                .eq('id', fightJson['fighter2_id'])
                .maybeSingle();
            
            if (fighter2Response != null) {
              fighter2 = Fighter.fromJson(fighter2Response);
            }
          }
          
          // Create fight with fighter details
          final fight = Fight.fromJson({
            ...fightJson,
            'fighter1': fighter1?.toJson(),
            'fighter2': fighter2?.toJson(),
          });
          
          fights.add(fight);
        } catch (e) {
          print('Error processing fight: $e');
        }
      }
      
      return fights;
    } catch (e) {
      print('Error getting fights: $e');
      return [];
    }
  }

  Future<Fight?> getFight(String id) async {
    try {
      final response = await _client
          .from('fights')
          .select('*')
          .eq('id', id)
          .maybeSingle();
      
      if (response == null) return null;
      
      // Get fighter1 details
      Fighter? fighter1;
      if (response['fighter1_id'] != null) {
        final fighter1Response = await _client
            .from('fighters')
            .select('*')
            .eq('id', response['fighter1_id'])
            .maybeSingle();
        
        if (fighter1Response != null) {
          fighter1 = Fighter.fromJson(fighter1Response);
        }
      }
      
      // Get fighter2 details
      Fighter? fighter2;
      if (response['fighter2_id'] != null) {
        final fighter2Response = await _client
            .from('fighters')
            .select('*')
            .eq('id', response['fighter2_id'])
            .maybeSingle();
        
        if (fighter2Response != null) {
          fighter2 = Fighter.fromJson(fighter2Response);
        }
      }
      
      // Create fight with fighter details
      return Fight.fromJson({
        ...response,
        'fighter1': fighter1?.toJson(),
        'fighter2': fighter2?.toJson(),
      });
    } catch (e) {
      print('Error getting fight: $e');
      return null;
    }
  }

  // Events
  Future<List<Event>> getEvents({
    bool upcoming = true,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _client
          .from('events')
          .select('*, fights(*)')
          .limit(limit)
          .range(offset, offset + limit - 1);
      
      return response.map((json) => Event.fromJson(json)).toList();
    } catch (e) {
      print('Error getting events: $e');
      return [];
    }
  }

  // User Profile
  Future<app_user.User?> getUserProfile(String userId) async {
    try {
      final response = await _client
          .from('user_profiles')
          .select()
          .eq('user_id', userId)
          .maybeSingle();
      
      return response != null ? app_user.User.fromJson(response) : null;
    } catch (e) {
      print('Error getting user profile: $e');
      return null;
    }
  }

  Future<app_user.User> updateUserProfile(String userId, Map<String, dynamic> data) async {
    try {
      final response = await _client
          .from('user_profiles')
          .update(data)
          .eq('user_id', userId)
          .select()
          .single();
      
      return app_user.User.fromJson(response);
    } catch (e) {
      print('Error updating user profile: $e');
      rethrow;
    }
  }

  // Predictions
  Future<Map<String, dynamic>> createPrediction(Map<String, dynamic> prediction) async {
    try {
      final response = await _client
          .from('predictions')
          .insert(prediction)
          .select()
          .single();
      
      return response;
    } catch (e) {
      print('Error creating prediction: $e');
      rethrow;
    }
  }

  Future<List<Map<String, dynamic>>> getUserPredictions(String userId) async {
    try {
      final response = await _client
          .from('predictions')
          .select('*, fights(*)')
          .eq('user_id', userId);
      
      return response;
    } catch (e) {
      print('Error getting user predictions: $e');
      return [];
    }
  }

  Future<List<Map<String, dynamic>>> getLeaderboard({int limit = 20}) async {
    try {
      final response = await _client
          .rpc('get_leaderboard', params: {'limit_count': limit});
      
      return response;
    } catch (e) {
      print('Error getting leaderboard: $e');
      return [];
    }
  }

  // Real-time subscriptions
  Stream<List<Fighter>> subscribeToFighters() {
    try {
      return _client
          .from('fighters')
          .stream(primaryKey: ['id'])
          .map((event) => event.map((json) => Fighter.fromJson(json)).toList());
    } catch (e) {
      print('Error subscribing to fighters: $e');
      return Stream.value([]);
    }
  }

  Stream<List<Fight>> subscribeToUpcomingFights() {
    try {
      return _client
          .from('fights')
          .stream(primaryKey: ['id'])
          .map((event) => event.map((json) => Fight.fromJson(json)).toList());
    } catch (e) {
      print('Error subscribing to fights: $e');
      return Stream.value([]);
    }
  }

  // Analytics
  Future<Map<String, dynamic>> getFighterStats(String fighterId) async {
    try {
      final response = await _client
          .rpc('get_fighter_stats', params: {'fighter_id': fighterId});
      
      return response;
    } catch (e) {
      print('Error getting fighter stats: $e');
      return {};
    }
  }

  Future<Map<String, dynamic>> getPredictionStats(String userId) async {
    try {
      final response = await _client
          .rpc('get_prediction_stats', params: {'user_id': userId});
      
      return response;
    } catch (e) {
      print('Error getting prediction stats: $e');
      return {};
    }
  }
} 