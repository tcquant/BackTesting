using System;
using System.Collections.Generic;
using MathNet.Numerics.LinearRegression;

public class RollingRegression
{
    public static List<double> CalculateRollingSlope(List<double> data, int windowSize)
    {
        List<double> slopes = new List<double>();

        // Iterate through the data with a rolling window
        for (int i = 0; i <= data.Count - windowSize; i++)
        {
            // Extract the window data for the current position
            List<double> window = data.GetRange(i, windowSize);

            // Generate x values (index positions) for the current window
            double[] x = new double[windowSize];
            double[] y = new double[windowSize];
            
            for (int j = 0; j < windowSize; j++)
            {
                x[j] = j;  // Index positions as x values
                y[j] = window[j];
            }

            // Perform linear regression to calculate slope
            var (slope, intercept) = SimpleRegression.Fit(x, y);

            // Store the slope in the list
            slopes.Add(slope);
        }

        return slopes;
    }

    public static void Main()
    {
        // Sample time series data
        List<double> timeSeriesData = new List<double> { 2, 3, 5, 6, 7, 8, 9, 10, 12, 13, 15 };

        // Window size for rolling regression
        int windowSize = 5;

        // Calculate the rolling slopes
        List<double> slopes = CalculateRollingSlope(timeSeriesData, windowSize);

        // Display the slopes
        Console.WriteLine("Rolling slopes:");
        foreach (double slope in slopes)
        {
            Console.WriteLine(slope);
        }
    }
}
