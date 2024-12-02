library(ggplot2)
library(readr)
library(dplyr)

# 读取清洗后的数据（指定 UTF-8 编码）
data_clean <- read_csv("data_clean.csv", locale = locale(encoding = "UTF-8"))

# 创建完整的时间范围和星期范围
time_levels <- c("12am", "1am", "2am", "3am", "4am", "5am", "6am", "7am", "8am", "9am", 
                 "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", 
                 "7pm", "8pm", "9pm", "10pm", "11pm")

day_levels <- c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# 确保时间和星期列是有序的
data_clean <- data_clean %>%
  mutate(
    Time = factor(gsub(" ", "", Time), levels = time_levels), # 去除空格并转换为因子
    Day = factor(Day, levels = day_levels)
  )

# 补全缺失时间和星期的组合，并填补繁忙度为 0
data_clean <- data_clean %>%
  complete(Day, Time, fill = list(Busyness = 0))

# 绘制热力图
ggplot(data_clean, aes(x = Time, y = Day, fill = Busyness)) +
  geom_tile(color = "white") +
  scale_fill_gradientn(colors = c("lightblue", "lightgreen", "pink", "orange"), name = "Busyness (%)") +  # 自定义渐变色
  labs(
    title = "Clementi Mall Weekly Busyness Heatmap", 
    x = "Time", 
    y = "Day"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 12, face = "bold"),  # 标题居中，设置字体大小
    axis.text.x = element_text(angle = 45, hjust = 1))

ggsave("Clementi Mall_heatmap.jpg", width = 10, height = 7)# 保存图片

