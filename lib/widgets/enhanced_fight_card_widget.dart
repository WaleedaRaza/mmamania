import 'package:flutter/material.dart';
import '../models/fight.dart';

class EnhancedFightCardWidget extends StatelessWidget {
  final Fight fight;
  final VoidCallback? onTap;
  final bool showEventInfo;

  const EnhancedFightCardWidget({
    Key? key,
    required this.fight,
    this.onTap,
    this.showEventInfo = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.06)),
        gradient: _getFightGradient(),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.35), blurRadius: 16, offset: Offset(0, 10)),
        ],
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildFightHeader(),
              SizedBox(height: 12),
              _buildWeightClass(),
              SizedBox(height: 8),
              _buildFightInfo(),
              SizedBox(height: 8),
              _buildMethodInfo(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFightHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // Fight Order Badge
        Container(
          padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: _getFightOrderColor(),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            _getFightOrderText(),
            style: TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        
        // Status Badge
        Container(
          padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: _getStatusColor(),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            fight.getStatusDisplay() == 'UPCOMING' ? '🔜 UPCOMING' : '✅ COMPLETED',
            style: TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildWeightClass() {
    return Text(
      fight.weightClass,
      style: TextStyle(
        color: Colors.white70,
        fontSize: 14,
        fontWeight: FontWeight.w500,
      ),
    );
  }

  Widget _buildFightInfo() {
    // Check if we have winner and loser names (not null and not empty)
    final hasWinnerLoser = (fight.winnerName != null && fight.winnerName!.isNotEmpty) && 
                          (fight.loserName != null && fight.loserName!.isNotEmpty);
    
    if (hasWinnerLoser) {
      // Show winner vs loser format
      return Row(
        children: [
          Expanded(
            child: _buildFighterInfo(
              name: fight.winnerName!,
              isWinner: true,
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.green.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              'def.',
              style: TextStyle(
                color: Colors.green,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          Expanded(
            child: _buildFighterInfo(
              name: fight.loserName!,
              isWinner: false,
            ),
          ),
        ],
      );
    } else {
      // Show scheduled fight format - try to get fighter names from various sources
      final fighter1Name = fight.getFighter1Name() ?? 'TBD';
      final fighter2Name = fight.getFighter2Name() ?? 'TBD';
      
      return Row(
        children: [
          Expanded(
            child: _buildFighterInfo(
              name: fighter1Name,
              isWinner: null,
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.orange.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              'vs',
              style: TextStyle(
                color: Colors.orange,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          Expanded(
            child: _buildFighterInfo(
              name: fighter2Name,
              isWinner: null,
            ),
          ),
        ],
      );
    }
  }

  Widget _buildFighterInfo({required String name, required bool? isWinner}) {
    Color textColor = Colors.white;
    FontWeight fontWeight = FontWeight.normal;
    
    if (isWinner == true) {
      textColor = Colors.green;
      fontWeight = FontWeight.bold;
    } else if (isWinner == false) {
      textColor = Colors.red;
    }
    
    return Text(
      name,
      style: TextStyle(
        color: textColor,
        fontSize: 16,
        fontWeight: fontWeight,
      ),
      textAlign: TextAlign.center,
      overflow: TextOverflow.ellipsis,
    );
  }

  Widget _buildMethodInfo() {
    final method = fight.getMethodDisplay();
    final roundTime = fight.getRoundTimeDisplay();
    
    if (method == 'TBD' && roundTime.isEmpty) {
      return SizedBox.shrink();
    }
    
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // Method
        if (method != 'TBD')
          Expanded(
            child: Text(
              method,
              style: TextStyle(
                color: Colors.white70,
                fontSize: 12,
                fontStyle: FontStyle.italic,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        
        // Round and Time
        if (roundTime.isNotEmpty)
          Text(
            roundTime,
            style: TextStyle(
              color: Colors.white70,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
      ],
    );
  }

  Color _getFightOrderColor() {
    if (fight.isMainEvent) {
      return Colors.red.shade700;
    } else if (fight.isCoMainEvent) {
      return Colors.orange.shade700;
    } else {
      return Colors.blue.shade700;
    }
  }

  String _getFightOrderText() {
    if (fight.isMainEvent) {
      return 'MAIN EVENT';
    } else if (fight.isCoMainEvent) {
      return 'CO-MAIN';
    } else {
      return '#${fight.getDisplayOrder()}';
    }
  }

  Color _getStatusColor() {
    if (fight.winnerName != null && fight.loserName != null) {
      return Colors.green;
    } else {
      return Colors.orange;
    }
  }

  LinearGradient _getFightGradient() {
    if (fight.isMainEvent) {
      return LinearGradient(
        colors: [Color(0xFF1A0E0E), Color(0xFF300D0D)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );
    } else if (fight.isCoMainEvent) {
      return LinearGradient(
        colors: [Color(0xFF261706), Color(0xFF3A2109)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );
    } else {
      return LinearGradient(
        colors: [Color(0xFF121212), Color(0xFF1C1C1C)],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      );
    }
  }
}

// Enhanced Fight Card List Widget for displaying multiple fights
class EnhancedFightCardListWidget extends StatelessWidget {
  final List<Fight> fights;
  final VoidCallback? onFightTap;
  final bool showEventInfo;

  const EnhancedFightCardListWidget({
    Key? key,
    required this.fights,
    this.onFightTap,
    this.showEventInfo = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Sort fights by order
    final sortedFights = List<Fight>.from(fights)
      ..sort((a, b) => a.getDisplayOrder().compareTo(b.getDisplayOrder()));

    return ListView.builder(
      shrinkWrap: true,
      physics: NeverScrollableScrollPhysics(),
      itemCount: sortedFights.length,
      itemBuilder: (context, index) {
        final fight = sortedFights[index];
        return EnhancedFightCardWidget(
          fight: fight,
          onTap: onFightTap,
          showEventInfo: showEventInfo,
        );
      },
    );
  }
} 