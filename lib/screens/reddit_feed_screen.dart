import 'package:flutter/material.dart';

class RedditFeedScreen extends StatefulWidget {
  const RedditFeedScreen({super.key});

  @override
  _RedditFeedScreenState createState() => _RedditFeedScreenState();
}

class _RedditFeedScreenState extends State<RedditFeedScreen> {
  int _selectedFilter = 0;
  final List<String> _filters = ['Hot', 'New', 'Top', 'Rising'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.red.shade900,
              Colors.red.shade800,
              Colors.black,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header Section
              Container(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.reddit,
                          color: Colors.white,
                          size: 32,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          'Reddit Feed',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Latest from r/MMA & r/UFC',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ),
              
              // Filter Selector
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(25),
                ),
                child: Row(
                  children: _filters.asMap().entries.map((entry) {
                    int index = entry.key;
                    String filter = entry.value;
                    bool isSelected = _selectedFilter == index;
                    
                    return Expanded(
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _selectedFilter = index;
                          });
                        },
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                          decoration: BoxDecoration(
                            gradient: isSelected
                                ? LinearGradient(
                                    colors: [Colors.white, Colors.white.withOpacity(0.9)],
                                  )
                                : null,
                            borderRadius: BorderRadius.circular(25),
                          ),
                          child: Text(
                            filter,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: isSelected
                                  ? Colors.red.shade900
                                  : Colors.white,
                              fontWeight: isSelected
                                  ? FontWeight.bold
                                  : FontWeight.normal,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
              
              const SizedBox(height: 20),
              
              // Reddit Posts
              Expanded(
                child: Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  child: ListView.builder(
                    padding: const EdgeInsets.only(bottom: 20),
                    itemCount: 15,
                    itemBuilder: (context, index) {
                      return _buildRedditPost(index);
                    },
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRedditPost(int index) {
    bool isHot = index % 4 == 0;
    bool isDiscussion = index % 3 == 0;
    bool isNews = index % 5 == 0;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white,
            Colors.grey.shade50,
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Post Header
            Row(
              children: [
                CircleAvatar(
                  radius: 16,
                  backgroundColor: Colors.red.shade100,
                  child: Icon(Icons.reddit, color: Colors.red.shade600, size: 16),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'r/MMA',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                          color: Colors.grey.shade800,
                        ),
                      ),
                      Text(
                        'Posted by u/mma_fan_${index + 1} • ${index + 1}h ago',
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                if (isHot)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.orange.shade100,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.orange.shade300),
                    ),
                    child: Text(
                      'HOT',
                      style: TextStyle(
                        color: Colors.orange.shade700,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            // Post Title
            Text(
              _getPostTitle(index),
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: Colors.grey.shade800,
              ),
            ),
            
            const SizedBox(height: 8),
            
            // Post Content
            if (isDiscussion || isNews)
              Text(
                _getPostContent(index),
                style: TextStyle(
                  color: Colors.grey.shade600,
                  fontSize: 14,
                ),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            
            const SizedBox(height: 12),
            
            // Post Stats
            Row(
              children: [
                Icon(Icons.arrow_upward, color: Colors.orange.shade600, size: 16),
                const SizedBox(width: 4),
                Text(
                  '${(index + 1) * 127}',
                  style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: 16),
                Icon(Icons.comment, color: Colors.grey.shade600, size: 16),
                const SizedBox(width: 4),
                Text(
                  '${(index + 1) * 23}',
                  style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(width: 16),
                Icon(Icons.share, color: Colors.grey.shade600, size: 16),
                const SizedBox(width: 4),
                Text(
                  '${(index + 1) * 5}',
                  style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 12,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getPostTypeColor(index).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _getPostTypeColor(index)),
                  ),
                  child: Text(
                    _getPostType(index),
                    style: TextStyle(
                      color: _getPostTypeColor(index),
                      fontWeight: FontWeight.bold,
                      fontSize: 10,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _getPostTitle(int index) {
    List<String> titles = [
      'Islam Makhachev vs Charles Oliveira 2 confirmed for UFC 300',
      'What\'s your prediction for the main event tonight?',
      'Just watched the press conference - thoughts?',
      'Fighter X calls out Fighter Y after last night\'s win',
      'UFC rankings updated - major changes in lightweight division',
      'Behind the scenes: Training camp footage',
      'Fight of the night candidate from last weekend',
      'Champion responds to challenger\'s comments',
      'New fight announcement - who wins?',
      'Post-fight interview highlights',
      'Training partner reveals game plan details',
      'Fighter retires after 15-year career',
      'Controversial decision sparks debate',
      'Injury update: Fighter out for 6 months',
      'Fight week: Final predictions thread',
    ];
    return titles[index % titles.length];
  }

  String _getPostContent(int index) {
    List<String> contents = [
      'The UFC has officially announced that Islam Makhachev will defend his lightweight title against Charles Oliveira at UFC 300. This is a rematch of their 2022 fight where Makhachev won by submission.',
      'I think this is going to be a completely different fight. Oliveira has improved his striking significantly and I believe he has the edge on the feet.',
      'The energy in the room was electric. Both fighters looked confident and ready. The trash talk was minimal but respectful.',
      'After his impressive victory last night, Fighter X wasted no time calling out the current champion. This could be an interesting matchup.',
      'The lightweight division has seen some major shakeups. Several fighters have moved up or down in the rankings.',
    ];
    return contents[index % contents.length];
  }

  String _getPostType(int index) {
    List<String> types = ['NEWS', 'DISCUSSION', 'PREDICTION', 'HIGHLIGHT', 'ANNOUNCEMENT'];
    return types[index % types.length];
  }

  Color _getPostTypeColor(int index) {
    List<Color> colors = [
      Colors.blue,
      Colors.green,
      Colors.orange,
      Colors.purple,
      Colors.red,
    ];
    return colors[index % colors.length];
  }
} 