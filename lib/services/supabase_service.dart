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

  // Fights - FIXED for new schema with direct fighter names
  Future<List<Fight>> getFights({
    bool upcoming = true,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      print('🚀 FIXED: Loading fights with new schema (winner_name/loser_name)');
      
      // Get all fights in one query - no need for separate fighter loading
      final fightsResponse = await _client
          .from('fights')
          .select('*')
          .limit(limit)
          .range(offset, offset + limit - 1);
      
      if (fightsResponse.isEmpty) {
        print('📊 No fights found');
        return [];
      }
      
      // Create fights directly - no separate fighter loading needed
      List<Fight> fights = [];
      for (var fightJson in fightsResponse) {
        try {
          // The Fight.fromJson method handles winner_name/loser_name directly
          final fight = Fight.fromJson(fightJson);
          fights.add(fight);
        } catch (e) {
          print('Error processing fight: $e');
        }
      }
      
      print('🎉 FIXED: Loaded ${fights.length} fights with new schema');
      return fights;
    } catch (e) {
      print('Error getting fights: $e');
      return [];
    }
  }

  // Get fights for a specific event - FIXED for new schema
  Future<List<Fight>> getFightsForEvent(String eventId) async {
    try {
      print('🚀 FIXED: Loading fights for event $eventId with proper ordering');
      
      // Get all fights for this event ordered by fight_order (main event first)
      final fightsResponse = await _client
          .from('fights')
          .select('*')
          .eq('event_id', eventId)
          .order('fight_order', ascending: true); // Order by fight order (1 = main event)
      
      if (fightsResponse.isEmpty) {
        print('📊 No fights found for event $eventId');
        return [];
      }
      
      // Create fights with direct fighter names
      List<Fight> fights = [];
      for (var fightJson in fightsResponse) {
        try {
          final fight = Fight.fromJson(fightJson);
          fights.add(fight);
        } catch (e) {
          print('Error processing fight: $e');
        }
      }
      
      print('✅ FIXED: Loaded ${fights.length} fights for event $eventId');
      return fights;
    } catch (e) {
      print('Error getting fights for event: $e');
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
      
      // The Fight.fromJson method now handles fighter1_name and fighter2_name directly
      // No need to load separate fighter records
      return Fight.fromJson(response);
    } catch (e) {
      print('Error getting fight: $e');
      return null;
    }
  }

  // Events - OPTIMIZED to prevent duplicates and ordered by date
  Future<List<Event>> getEvents({
    bool upcoming = true,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      print('🚀 OPTIMIZED: Loading events with deduplication and date ordering (client-side filters)');

      // Fetch ordered by date desc; if limit <= 0, fetch ALL via pagination
      final List<Map<String, dynamic>> rows = [];

      const int pageSize = 200;
      if (limit <= 0) {
        int start = 0;
        while (true) {
          final page = await _client
              .from('events')
              .select('*')
              .order('date', ascending: false)
              .range(start, start + pageSize - 1);

          if (page.isEmpty) break;
          rows.addAll(List<Map<String, dynamic>>.from(page));

          // Advance window
          start += pageSize;

          // Safety cap to avoid runaway loops (can adjust higher as needed)
          if (start > 5000) break;
        }
        print('📦 Fetched all events via pagination: ${rows.length}');
      } else {
        final page = await _client
            .from('events')
            .select('*')
            .order('date', ascending: false)
            .range(offset, offset + limit - 1);
        rows.addAll(List<Map<String, dynamic>>.from(page));
      }

      // Map -> Event (Event.fromJson handles null/invalid dates)
      final allEvents = rows.map<Event>((e) => Event.fromJson(e)).toList();

      // Deduplicate by name
      final Map<String, Event> unique = {};
      for (final ev in allEvents) {
        unique.putIfAbsent(ev.title, () => ev);
      }

      // Client-side filter by upcoming/past using parsed DateTime
      final now = DateTime.now();
      List<Event> events = unique.values
          .where((ev) => upcoming
              ? ev.date.isAfter(now) || ev.date.isAtSameMomentAs(now)
              : ev.date.isBefore(now) || ev.date.isAtSameMomentAs(now))
          .toList();

      // Final ordering
      events.sort((a, b) => upcoming ? a.date.compareTo(b.date) : b.date.compareTo(a.date));

      print('✅ OPTIMIZED: Loaded ${events.length} unique events ordered by date');
      return events;
    } catch (e) {
      print('Error getting events: $e');
      return [];
    }
  }

  Future<List<Event>> searchEvents(String query, {int limit = 50, int offset = 0}) async {
    try {
      final q = query.trim();
      if (q.isEmpty || q.length < 3) return [];
      final qLower = q.toLowerCase();

      bool containsWholeWord(String? text, String needle) {
        if (text == null) return false;
        final t = text.toLowerCase();
        // Fast path
        if (t == needle) return true;
        final tokens = t.split(RegExp(r'[^a-z0-9]+'))..removeWhere((e) => e.isEmpty);
        return tokens.contains(needle);
      }

      // 1) Match by fighter names within fights (strict whole-word)
      final fightsMatch = await _client
          .from('fights')
          .select('event_id,winner_name,loser_name')
          .or('winner_name.ilike.%$q%,loser_name.ilike.%$q%');

      final Set<String> eventIds = {};
      for (final f in fightsMatch) {
        final id = f['event_id'] as String?;
        if (id == null) continue;
        final wn = f['winner_name'] as String?;
        final ln = f['loser_name'] as String?;
        if (containsWholeWord(wn, qLower) || containsWholeWord(ln, qLower)) {
          eventIds.add(id);
        }
      }

      // 2) Include events where the card title contains the query as a whole word
      final titlePage = await _client
          .from('events')
          .select('id,name,date')
          .ilike('name', '%$q%')
          .order('date', ascending: false)
          .limit(limit)
          .range(offset, offset + limit - 1);
      for (final e in titlePage) {
        final id = e['id'] as String?;
        final name = e['name'] as String?;
        if (id != null && containsWholeWord(name, qLower)) {
          eventIds.add(id);
        }
      }

      if (eventIds.isEmpty) return [];

      // Fetch ONLY these events
      final idList = eventIds.toList();
      List<Map<String, dynamic>> rows = [];
      const int chunk = 200;
      for (int i = 0; i < idList.length; i += chunk) {
        final sub = idList.sublist(i, i + chunk > idList.length ? idList.length : i + chunk);
        final filter = sub.map((id) => 'id.eq.$id').join(',');
        final page = await _client
            .from('events')
            .select('*')
            .or(filter)
            .order('date', ascending: false);
        rows.addAll(List<Map<String, dynamic>>.from(page));
      }

      // Dedupe and sort
      final Map<String, Event> unique = {};
      for (final r in rows) {
        final ev = Event.fromJson(r);
        unique[ev.id] = ev;
      }
      final result = unique.values.toList()
        ..sort((a, b) => b.date.compareTo(a.date));

      return result;
    } catch (e) {
      print('Error searching events: $e');
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