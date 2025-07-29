import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/fighter.dart';
import '../models/fight.dart';
import '../models/event.dart';
import '../models/ranking_item.dart';
import '../models/prediction.dart';
import '../models/user_stats.dart';

class SimpleDatabaseService {
  static SimpleDatabaseService? _instance;
  static SimpleDatabaseService get instance => _instance ??= SimpleDatabaseService._();
  
  late final SupabaseClient _client;
  
  SimpleDatabaseService._() {
    _client = Supabase.instance.client;
  }

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
      
      List<Fighter> fighters = response.map((json) => Fighter.fromJson(json)).toList();
      
      // Filter in Dart instead of SQL to avoid method chaining issues
      if (weightClass != null) {
        fighters = fighters.where((f) => f.weightClass == weightClass).toList();
      }
      
      if (activeOnly) {
        fighters = fighters.where((f) => f.isActive).toList();
      }
      
      return fighters;
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
  Future<List<RankingItem>> getRankingItems(String weightClass) async {
    try {
      print('🔍 Querying ranking items for weight class: $weightClass');
      
      final response = await _client
          .from('rankings')
          .select('*, fighters(*)')
          .eq('weight_class', weightClass)
          .order('rank_position', ascending: true);  // Champions (rank 0/1) first, then contenders
      
      print('📊 Raw response: ${response.length} items');
      
      List<RankingItem> rankingItems = [];
      for (var json in response) {
        try {
          final rankingItem = RankingItem.fromJson(json);
          rankingItems.add(rankingItem);
        } catch (e) {
          print('❌ Error parsing ranking item: $e');
        }
      }
      
      print('✅ Returning ${rankingItems.length} ranking items');
      return rankingItems;
    } catch (e) {
      print('❌ Error getting ranking items: $e');
      return [];
    }
  }

  Future<List<Fighter>> getRankings(String weightClass) async {
    try {
      print('🔍 Querying rankings for weight class: $weightClass');
      
      final response = await _client
          .from('rankings')
          .select('*, fighters(*)')
          .eq('weight_class', weightClass)
          .order('rank_position');
      
      print('📊 Raw response: ${response.length} items');
      
      List<Fighter> fighters = [];
      for (var json in response) {
        final fighterData = json['fighters'] as Map<String, dynamic>?;
        if (fighterData != null) {
          try {
            final fighter = Fighter.fromJson(fighterData);
            fighters.add(fighter);
          } catch (e) {
            print('❌ Error parsing fighter: $e');
          }
        } else {
          print('⚠️ No fighter data for ranking: ${json['id']}');
        }
      }
      
      print('✅ Returning ${fighters.length} fighters');
      return fighters;
    } catch (e) {
      print('❌ Error getting rankings: $e');
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
      print('🔍 Getting fights from Supabase (upcoming: $upcoming, limit: $limit)');
      
      // First get all fights
      final response = await _client
          .from('fights')
          .select('*')
          .limit(limit)
          .range(offset, offset + limit - 1);
      
      print('📊 Raw fights response: ${response.length} fights');
      
      List<Fight> fights = [];
      
      // For each fight, get the fighter details separately
      for (var fightJson in response) {
        try {
          print('🔍 Processing fight: ${fightJson['id']} - status: ${fightJson['status']}');
          
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
              print('✅ Found fighter1: ${fighter1.name}');
            } else {
              print('❌ Fighter1 not found: ${fightJson['fighter1_id']}');
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
              print('✅ Found fighter2: ${fighter2.name}');
            } else {
              print('❌ Fighter2 not found: ${fightJson['fighter2_id']}');
            }
          }
          
          // Create fight with fighter details
          final fight = Fight.fromJson({
            ...fightJson,
            'fighter1': fighter1 != null ? fighter1.toJson() : null,
            'fighter2': fighter2 != null ? fighter2.toJson() : null,
          });
          
          fights.add(fight);
          print('✅ Added fight: ${fighter1?.name} vs ${fighter2?.name}');
        } catch (e) {
          print('Error processing fight: $e');
        }
      }
      
      print('📊 Total fights before filtering: ${fights.length}');
      
      // Filter in Dart instead of SQL
      if (upcoming) {
        fights = fights.where((f) => f.status == 'scheduled').toList();
        print('📊 Fights after filtering for upcoming: ${fights.length}');
      }
      
      print('🎉 Returning ${fights.length} fights');
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
        'fighter1': fighter1 != null ? fighter1.toJson() : null,
        'fighter2': fighter2 != null ? fighter2.toJson() : null,
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
      
      List<Event> events = response.map((json) => Event.fromJson(json)).toList();
      
      // Filter in Dart instead of SQL
      if (upcoming) {
        events = events.where((e) => e.type == 'upcoming').toList();
      }
      
      return events;
    } catch (e) {
      print('Error getting events: $e');
      return [];
    }
  }

  Future<Event?> getEvent(String id) async {
    try {
      final response = await _client
          .from('events')
          .select('*, fights(*)')
          .eq('id', id)
          .maybeSingle();
      
      return response != null ? Event.fromJson(response) : null;
    } catch (e) {
      print('Error getting event: $e');
      return null;
    }
  }

  // Predictions
  Future<List<Prediction>> getUserPredictions(String userId) async {
    try {
      final response = await _client
          .from('predictions')
          .select('*, fights(*)')
          .eq('user_id', userId)
          .order('created_at', ascending: false);
      
      return response.map((json) => Prediction.fromJson(json)).toList();
    } catch (e) {
      print('Error getting user predictions: $e');
      return [];
    }
  }

  Future<Prediction?> getPrediction(String id) async {
    try {
      final response = await _client
          .from('predictions')
          .select('*, fights(*)')
          .eq('id', id)
          .maybeSingle();
      
      return response != null ? Prediction.fromJson(response) : null;
    } catch (e) {
      print('Error getting prediction: $e');
      return null;
    }
  }

  Future<Prediction?> createPrediction({
    required String userId,
    required String fightId,
    required String predictedWinnerId,
    String? predictedMethod,
    int? predictedRound,
  }) async {
    try {
      final response = await _client
          .from('predictions')
          .insert({
            'user_id': userId,
            'fight_id': fightId,
            'predicted_winner_id': predictedWinnerId,
            'predicted_method': predictedMethod,
            'predicted_round': predictedRound,
            'result': 'pending',
          })
          .select()
          .single();
      
      return Prediction.fromJson(response);
    } catch (e) {
      print('Error creating prediction: $e');
      return null;
    }
  }

  Future<bool> updatePredictionResult(String predictionId, PredictionResult result, {
    String? actualWinnerId,
    String? actualMethod,
    int? actualRound,
    int? eloChange,
  }) async {
    try {
      await _client
          .from('predictions')
          .update({
            'result': result.toString().split('.').last,
            'actual_winner_id': actualWinnerId,
            'actual_method': actualMethod,
            'actual_round': actualRound,
            'elo_change': eloChange,
          })
          .eq('id', predictionId);
      
      return true;
    } catch (e) {
      print('Error updating prediction result: $e');
      return false;
    }
  }

  // User Stats
  Future<UserStats?> getUserStats(String userId) async {
    try {
      final response = await _client
          .from('user_stats')
          .select()
          .eq('user_id', userId)
          .maybeSingle();
      
      if (response != null) {
        return UserStats.fromJson(response);
      } else {
        // Create default stats for new user
        final defaultStats = UserStats(
          userId: userId,
          lastPredictionDate: DateTime.now(),
        );
        
        final createdResponse = await _client
            .from('user_stats')
            .insert(defaultStats.toJson())
            .select()
            .single();
        
        return UserStats.fromJson(createdResponse);
      }
    } catch (e) {
      print('Error getting user stats: $e');
      return null;
    }
  }

  Future<bool> updateUserStats(UserStats stats) async {
    try {
      await _client
          .from('user_stats')
          .upsert(stats.toJson())
          .eq('user_id', stats.userId);
      
      return true;
    } catch (e) {
      print('Error updating user stats: $e');
      return false;
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

  Stream<List<Fight>> subscribeToFights() {
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

  Stream<List<Event>> subscribeToEvents() {
    try {
      return _client
          .from('events')
          .stream(primaryKey: ['id'])
          .map((event) => event.map((json) => Event.fromJson(json)).toList());
    } catch (e) {
      print('Error subscribing to events: $e');
      return Stream.value([]);
    }
  }

  // Database health check
  Future<bool> testConnection() async {
    try {
      await _client.from('fighters').select('count').limit(1);
      return true;
    } catch (e) {
      print('Database connection test failed: $e');
      return false;
    }
  }

  // Get database stats
  Future<Map<String, int>> getDatabaseStats() async {
    try {
      final fightersResponse = await _client.from('fighters').select('*');
      final fightsResponse = await _client.from('fights').select('*');
      final eventsResponse = await _client.from('events').select('*');
      final rankingsResponse = await _client.from('rankings').select('*');
      
      return {
        'fighters': fightersResponse.length,
        'fights': fightsResponse.length,
        'events': eventsResponse.length,
        'rankings': rankingsResponse.length,
      };
    } catch (e) {
      print('Error getting database stats: $e');
      return {};
    }
  }
} 