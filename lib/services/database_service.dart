import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/fighter.dart';
import '../models/fight.dart';
import '../models/event.dart';

class DatabaseService {
  static DatabaseService? _instance;
  static DatabaseService get instance => _instance ??= DatabaseService._();
  
  late final SupabaseClient _client;
  
  DatabaseService._() {
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
      var query = _client
          .from('fighters')
          .select()
          .limit(limit)
          .range(offset, offset + limit - 1);
      
      if (weightClass != null) {
        query = query.eq('weight_class', weightClass);
      }
      
      if (activeOnly) {
        query = query.eq('is_active', true);
      }
      
      final response = await query;
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
          .eq('weight_class', weightClass)
          .order('rank_position');
      
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
      var query = _client
          .from('fights')
          .select('*')
          .limit(limit)
          .range(offset, offset + limit - 1);
      
      if (upcoming) {
        query = query.eq('status', 'scheduled');
      }
      
      final response = await query;
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
      var query = _client
          .from('events')
          .select('*, fights(*)')
          .limit(limit)
          .range(offset, offset + limit - 1);
      
      if (upcoming) {
        query = query.eq('status', 'scheduled');
      }
      
      final response = await query;
      return response.map((json) => Event.fromJson(json)).toList();
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
      await _client.from('fighters').select('count').limit(1).execute();
      return true;
    } catch (e) {
      print('Database connection test failed: $e');
      return false;
    }
  }

  // Get database stats
  Future<Map<String, int>> getDatabaseStats() async {
    try {
      final fightersCount = await _client.from('fighters').select('count').execute();
      final fightsCount = await _client.from('fights').select('count').execute();
      final eventsCount = await _client.from('events').select('count').execute();
      final rankingsCount = await _client.from('rankings').select('count').execute();
      
      return {
        'fighters': fightersCount.count ?? 0,
        'fights': fightsCount.count ?? 0,
        'events': eventsCount.count ?? 0,
        'rankings': rankingsCount.count ?? 0,
      };
    } catch (e) {
      print('Error getting database stats: $e');
      return {};
    }
  }
} 