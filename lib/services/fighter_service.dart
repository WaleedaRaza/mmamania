import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/fighter.dart';

class FighterService {
  static final FighterService _instance = FighterService._internal();
  factory FighterService() => _instance;
  FighterService._internal();

  List<Fighter> _fighters = [];
  Map<String, Fighter> _fightersById = {};
  bool _isLoaded = false;

  bool get isLoaded => _isLoaded;

  Future<void> loadFighterData() async {
    if (_isLoaded) return;

    try {
      final String jsonString = await rootBundle.loadString('assets/data/ufc_data.json');
      final Map<String, dynamic> jsonData = json.decode(jsonString);
      
      _fighters = [];
      _fightersById = {};

      if (jsonData['fighters'] != null) {
        for (var fighterJson in jsonData['fighters']) {
          try {
            final fighter = _createFighterFromJson(fighterJson);
            _fighters.add(fighter);
            _fightersById[fighter.id] = fighter;
          } catch (e) {
            print('Error parsing fighter: $e');
          }
        }
      }

      _isLoaded = true;
      print('✅ Loaded ${_fighters.length} fighter profiles');
      
    } catch (e) {
      print('❌ Error loading fighter data: $e');
      _isLoaded = false;
    }
  }

  Fighter _createFighterFromJson(Map<String, dynamic> json) {
    // Handle the scraped data structure
    final ranking = json['ranking'] ?? {};
    final stats = json['stats'] ?? {};
    final personalInfo = json['personal_info'] ?? {};
    final fightHistory = json['fight_history'] ?? [];
    
    return Fighter(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      division: json['division'] ?? '',
      record: Record(
        wins: json['record']?['wins'] ?? 0,
        losses: json['record']?['losses'] ?? 0,
        draws: json['record']?['draws'] ?? 0,
      ),
      imageUrl: null,
      status: personalInfo['status'],
      placeOfBirth: personalInfo['place_of_birth'],
      trainingAt: personalInfo['training_at'],
      fightingStyle: personalInfo['fighting_style'],
      age: personalInfo['age'],
      height: personalInfo['height']?.toDouble(),
      weight: personalInfo['weight']?.toDouble(),
      octagonDebut: personalInfo['octagon_debut'],
      reach: personalInfo['reach']?.toDouble(),
      legReach: personalInfo['leg_reach']?.toDouble(),
      stats: FighterStats(
        fightWinStreak: stats['fight_win_streak'] ?? 0,
        winsByKnockout: stats['wins_by_knockout'] ?? 0,
        winsBySubmission: stats['wins_by_submission'] ?? 0,
        strikingAccuracy: (stats['striking_accuracy'] ?? 0).toDouble(),
        sigStrikesLanded: stats['sig_strikes_landed'] ?? 0,
        sigStrikesAttempted: stats['sig_strikes_attempted'] ?? 0,
        takedownAccuracy: (stats['takedown_accuracy'] ?? 0).toDouble(),
        takedownsLanded: stats['takedowns_landed'] ?? 0,
        takedownsAttempted: stats['takedowns_attempted'] ?? 0,
        sigStrikesLandedPerMin: (stats['sig_strikes_landed_per_min'] ?? 0).toDouble(),
        sigStrikesAbsorbedPerMin: (stats['sig_strikes_absorbed_per_min'] ?? 0).toDouble(),
        takedownAvgPer15Min: (stats['takedown_avg_per_15_min'] ?? 0).toDouble(),
        submissionAvgPer15Min: (stats['submission_avg_per_15_min'] ?? 0).toDouble(),
        sigStrikesDefense: (stats['sig_strikes_defense'] ?? 0).toDouble(),
        takedownDefense: (stats['takedown_defense'] ?? 0).toDouble(),
        knockdownAvg: (stats['knockdown_avg'] ?? 0).toDouble(),
        averageFightTime: stats['average_fight_time'] ?? '0:00',
      ),
      fightHistory: (fightHistory as List<dynamic>)
          .map((fight) => FightResult(
                result: fight['result'] ?? '',
                opponent: fight['opponent'] ?? '',
                event: fight['event'] ?? '',
                date: fight['date'] ?? '',
                round: fight['round'] ?? '',
                time: fight['time'] ?? '',
                method: fight['method'] ?? '',
              ))
          .toList(),
    );
  }

  List<Fighter> getAllFighters() {
    return List.from(_fighters);
  }

  Fighter? getFighterById(String id) {
    return _fightersById[id];
  }

  Fighter? getFighterByName(String name) {
    return _fighters.firstWhere(
      (fighter) => fighter.name.toLowerCase() == name.toLowerCase(),
      orElse: () => Fighter.empty(),
    );
  }

  List<Fighter> getFightersByDivision(String division) {
    return _fighters.where((fighter) => fighter.division == division).toList();
  }

  List<Fighter> searchFighters(String query) {
    if (query.isEmpty) return [];
    
    return _fighters.where((fighter) =>
        fighter.name.toLowerCase().contains(query.toLowerCase()) ||
        fighter.division.toLowerCase().contains(query.toLowerCase()) ||
        fighter.fightingStyle?.toLowerCase().contains(query.toLowerCase()) == true
    ).toList();
  }

  void clearData() {
    _fighters.clear();
    _fightersById.clear();
    _isLoaded = false;
  }
} 