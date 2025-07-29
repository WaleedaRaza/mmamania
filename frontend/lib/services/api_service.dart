import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/user.dart';
import '../models/fight.dart';
import '../models/fighter.dart';
import '../models/prediction.dart';
import '../models/debate.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000';
  static const FlutterSecureStorage _storage = FlutterSecureStorage();
  
  late final Dio _dio;
  
  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ));
    
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Add auth token to requests
        final token = await _storage.read(key: 'auth_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) {
        // Handle common errors
        if (error.response?.statusCode == 401) {
          // Token expired or invalid
          _storage.delete(key: 'auth_token');
        }
        handler.next(error);
      },
    ));
  }

  // Authentication
  Future<String> login(String email, String password) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'username': email,
        'password': password,
      });
      
      final token = response.data['access_token'];
      await _storage.write(key: 'auth_token', value: token);
      return token;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<User> register(String username, String email, String password) async {
    try {
      final response = await _dio.post('/auth/register', data: {
        'username': username,
        'email': email,
        'password': password,
      });
      
      return User.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: 'auth_token');
  }

  // User Management
  Future<User> getCurrentUser() async {
    try {
      final response = await _dio.get('/users/me');
      return User.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<User> updateUser(Map<String, dynamic> userData) async {
    try {
      final response = await _dio.put('/users/me', data: userData);
      return User.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Fights
  Future<List<Fight>> getFights({bool upcoming = true, int limit = 20, int skip = 0}) async {
    try {
      final response = await _dio.get('/fights/', queryParameters: {
        'upcoming': upcoming,
        'limit': limit,
        'skip': skip,
      });
      
      return (response.data as List)
          .map((json) => Fight.fromJson(json))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Fight> getFight(String fightId) async {
    try {
      final response = await _dio.get('/fights/$fightId');
      return Fight.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<Fight>> getUpcomingMainEvents() async {
    try {
      final response = await _dio.get('/fights/upcoming/main-events');
      return (response.data as List)
          .map((json) => Fight.fromJson(json))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Fighters
  Future<List<Fighter>> getFighters({
    String? weightClass,
    bool activeOnly = true,
    int limit = 50,
    int skip = 0,
  }) async {
    try {
      final response = await _dio.get('/fighters/', queryParameters: {
        if (weightClass != null) 'weight_class': weightClass,
        'active_only': activeOnly,
        'limit': limit,
        'skip': skip,
      });
      
      return (response.data as List)
          .map((json) => Fighter.fromJson(json))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Fighter> getFighter(String fighterId) async {
    try {
      final response = await _dio.get('/fighters/$fighterId');
      return Fighter.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<String>> getWeightClasses() async {
    try {
      final response = await _dio.get('/fighters/weight-classes/list');
      return (response.data as List).cast<String>();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getRankings(String weightClass) async {
    try {
      final response = await _dio.get('/fighters/rankings/$weightClass');
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<Map<String, dynamic>>> searchFighters(String name) async {
    try {
      final response = await _dio.get('/fighters/search/$name');
      return (response.data as List).cast<Map<String, dynamic>>();
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Predictions
  Future<Prediction> createPrediction(String fightId, Map<String, dynamic> predictionData) async {
    try {
      final response = await _dio.post('/fights/$fightId/predict', data: predictionData);
      return Prediction.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<Prediction>> getUserPredictions({int limit = 20, int skip = 0}) async {
    try {
      final response = await _dio.get('/predictions/', queryParameters: {
        'limit': limit,
        'skip': skip,
      });
      
      return (response.data as List)
          .map((json) => Prediction.fromJson(json))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getLeaderboard({String period = 'all', int limit = 20}) async {
    try {
      final response = await _dio.get('/predictions/leaderboard', queryParameters: {
        'period': period,
        'limit': limit,
      });
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getPredictionStats() async {
    try {
      final response = await _dio.get('/predictions/stats');
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Debates
  Future<List<DebateRoom>> getDebateRooms({
    String statusFilter = 'Active',
    int limit = 20,
    int skip = 0,
  }) async {
    try {
      final response = await _dio.get('/debates/', queryParameters: {
        'status_filter': statusFilter,
        'limit': limit,
        'skip': skip,
      });
      
      return (response.data as List)
          .map((json) => DebateRoom.fromJson(json))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<DebateRoom> createDebateRoom(Map<String, dynamic> debateData) async {
    try {
      final response = await _dio.post('/debates/', data: debateData);
      return DebateRoom.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<DebateRoom> getDebateRoom(String debateId) async {
    try {
      final response = await _dio.get('/debates/$debateId');
      return DebateRoom.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> joinDebateRoom(String debateId) async {
    try {
      await _dio.post('/debates/$debateId/join');
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> leaveDebateRoom(String debateId) async {
    try {
      await _dio.post('/debates/$debateId/leave');
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<DebateMessage>> getDebateMessages(String debateId, {int limit = 50, int skip = 0}) async {
    try {
      final response = await _dio.get('/debates/$debateId/messages', queryParameters: {
        'limit': limit,
        'skip': skip,
      });
      
      return (response.data as List)
          .map((json) => DebateMessage.fromJson(json))
          .toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<DebateMessage> createDebateMessage(String debateId, Map<String, dynamic> messageData) async {
    try {
      final response = await _dio.post('/debates/$debateId/messages', data: messageData);
      return DebateMessage.fromJson(response.data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  // ML Insights
  Future<Map<String, dynamic>> getFightPredictions(String fightId) async {
    try {
      final response = await _dio.get('/ml/fights/$fightId/predictions');
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getFighterAnalytics(String fighterId) async {
    try {
      final response = await _dio.get('/ml/fighters/$fighterId/analytics');
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getFightInsights(String fightId) async {
    try {
      final response = await _dio.get('/ml/fights/$fightId/insights');
      return response.data;
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Error handling
  Exception _handleError(dynamic error) {
    if (error is DioException) {
      if (error.response != null) {
        final statusCode = error.response!.statusCode;
        final data = error.response!.data;
        
        switch (statusCode) {
          case 400:
            return Exception(data['detail'] ?? 'Bad request');
          case 401:
            return Exception('Unauthorized');
          case 403:
            return Exception('Forbidden');
          case 404:
            return Exception('Not found');
          case 422:
            return Exception('Validation error');
          case 500:
            return Exception('Server error');
          default:
            return Exception('Network error');
        }
      } else {
        return Exception('Network error');
      }
    }
    return Exception('Unknown error');
  }
} 